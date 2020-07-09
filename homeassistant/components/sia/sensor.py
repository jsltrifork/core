"""Platform for sensor integration."""
import logging

import aiohttp
from aiohttp import BasicAuth, ClientSession

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_URL
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from .const import SIA_SCHEMA, CONF_PLUGIN, CONF_DEVICE_ID, CONF_ITEM_ID, CONF_SOURCES

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(SIA_SCHEMA)


async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    sia_url = config.get(CONF_URL)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    session = hass.helpers.aiohttp_client.async_get_clientsession()
    auth = aiohttp.BasicAuth(username, password=password)

    sources = config.get(CONF_SOURCES)
    entities = []
    for source in sources:
        item_id = source[CONF_ITEM_ID]
        device_id = source[CONF_DEVICE_ID]
        plugin = source[CONF_PLUGIN]

        # Get name and unit from SIA for source.
        url = (
            f"http://{sia_url}/api/plugins/{plugin}/devices/{device_id}/items/{item_id}"
        )
        try:
            response = await session.get(url, auth=auth)
            if response.status == 200:
                json = await response.json()

                name = json["name"]
                unit = json["unit"]
                entities.append(
                    SIASensor(
                        name, sia_url, plugin, device_id, item_id, session, auth, unit
                    )
                )
            else:
                _LOGGER.error(
                    "Could not find plug, device or item: %s, %s, %s",
                    plugin,
                    device_id,
                    item_id,
                )

        except aiohttp.ClientError as error:
            _LOGGER.error(
                "Could not set up source: %s, %s, %s", plugin, device_id, item_id
            )
            _LOGGER.debug(error)

    add_entities(
        entities, update_before_add=True,
    )


class SIASensor(Entity):
    """Representation of a Sensor."""

    _name: str = None
    _host: str = None
    _plugin: str = None
    _device_id: int = None
    _item_id: int = None
    _session: ClientSession = None
    _auth: BasicAuth = None
    _unit: str = None

    def __init__(self, name, host, plugin, device_id, item_id, session, auth, unit):
        """Initialize the sensor."""
        self._state = None
        self._host = host
        self._name = name
        self._plugin = plugin
        self._device_id = device_id
        self._item_id = item_id
        self._session = session
        self._auth = auth
        self._unit = unit

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    async def async_update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        # Construct URL.
        entity_url = f"http://{self._host}/api/plugins/{self._plugin}/devices/{self._device_id}/items/{self._item_id}/data"

        try:
            response = await self._session.get(entity_url, auth=self._auth)
            json = await response.json()
            self._state = json["values"][0]["value"]
            _LOGGER.info("Updating sensor %s", self._name)

        except aiohttp.ClientError as ex:
            _LOGGER.error("Could not get data for sensor %s:", self._name)
            _LOGGER.error(ex)
