"""Platform for sensor integration."""
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    add_entities(
        [SIASensor("Room11sensor", "172.31.100.129", "bacnet_ip", 2, 13)],
        update_before_add=True,
    )


class SIASensor(Entity):
    """Representation of a Sensor."""

    _name = None
    _host = None
    _plugin = None
    _device_id = None
    _item_id = None

    def __init__(self, name, host, plugin, device_id, item_id):
        """Initialize the sensor."""
        self._state = None
        self._host = host
        self._name = name
        self._plugin = plugin
        self._device_id = device_id
        self._item_id = item_id

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
        _LOGGER.info(url)

        json = await self._fetch_json(url)
        _LOGGER.info(json)

        # http://172.31.100.129/api/plugins/bacnet_ip/devices/2/items/13/data
        # "{{ value_json['values'][0]['value'] }}"
        self._state = json["values"][0]["value"]

    async def _fetch_json(self, url):
        auth = aiohttp.BasicAuth("Trifork", password="Trifork")
        # auth_header = auth.encode()

        async with aiohttp.ClientSession(auth=auth) as session:

            async with session.get(url) as response:
                return await response.json()
