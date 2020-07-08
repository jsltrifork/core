"""Platform for sensor integration."""
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
import aiohttp
from aiohttp import BasicAuth, ClientSession
import logging
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)


CONF_ATTRIBUTES = "Information provided by: https://futar.bkk.hu/"
CONF_STOPID = "stopId"
CONF_MINSAFTER = "minsAfter"
CONF_WHEELCHAIR = "wheelchair"
CONF_BIKES = "bikes"
CONF_IGNORENOW = "ignoreNow"

DEFAULT_NAME = "BKK Futar"
DEFAULT_ICON = "mdi:bus"
DEFAULT_UNIT = "min"


# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
#     {
#         vol.Required(CONF_STOPID): cv.string,
#         vol.Optional(CONF_MINSAFTER, default=20): cv.string,
#         vol.Optional(CONF_WHEELCHAIR, default=False): cv.boolean,
#         vol.Optional(CONF_BIKES, default=False): cv.boolean,
#         vol.Optional(CONF_IGNORENOW, default="false"): cv.boolean,
#         vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
#     }
# )


async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # name = config.get(CONF_NAME)
    # stopid = config.get(CONF_STOPID)
    # minsafter = config.get(CONF_MINSAFTER)
    # wheelchair = config.get(CONF_WHEELCHAIR)
    # bikes = config.get(CONF_BIKES)
    # ignorenow = config.get(CONF_IGNORENOW)

    session = hass.helpers.aiohttp_client.async_get_clientsession()
    auth = aiohttp.BasicAuth("Trifork", password="Trifork")

    add_entities(
        [
            SIASensor(
                "Room11sensor", "172.31.100.129", "bacnet_ip", 2, 13, session, auth
            )
        ],
        update_before_add=True,
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

    def __init__(self, name, host, plugin, device_id, item_id, session, auth):
        """Initialize the sensor."""
        self._state = None
        self._host = host
        self._name = name
        self._plugin = plugin
        self._device_id = device_id
        self._item_id = item_id
        self._session = session
        self._auth = auth

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
        return TEMP_CELSIUS

    async def async_update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        # Construct URL.
        url = f"http://{self._host}/api/plugins/{self._plugin}/devices/{self._device_id}/items/{self._item_id}/data"

        try:
            response = await self._session.get(url, auth=self._auth)
            json = await response.json()
            self._state = json["values"][0]["value"]
            _LOGGER.info("Updating sensor %s", self._name)

        except aiohttp.ClientError as ex:
            _LOGGER.error("Could not get data for sensor %s:", self._name)
            _LOGGER.error(ex)
