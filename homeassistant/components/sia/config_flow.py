from homeassistant import config_entries
from .const import DOMAIN
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_URL
from homeassistant import config_entries
from aiohttp import ClientSession, BasicAuth

_LOGGER = logging.getLogger(__name__)

CONF_SOURCES = "sources"
CONF_DEVICE_ID = "deviceId"
CONF_PLUGIN = "plugin"
CONF_ITEM_ID = "itemId"

USER_SCHEMA = {
    vol.Required(CONF_URL): str,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
}


class SIAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    url = None
    username = None
    password = None

    sources = None
    has_sources = False

    async def async_step_user(self, user_input=None):
        if not user_input:
            # Propmt user for url, username and password.
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema(USER_SCHEMA)
            )

        url = "172.31.100.129"  # user_input[CONF_URL]
        username = "Trifork"  # user_input[CONF_USERNAME]
        password = "Trifork"  # user_input[CONF_PASSWORD]

        sensors = await self.get_sensor_info(url, username, password)

        sensor_schema = vol.Schema(schema={})
        for sensor in sensors[:10]:
            sensor_schema.extend({vol.Optional(sensor["name"]): bool})

        return self.async_show_form(step_id="sources", data_schema=sensor_schema)

    async def async_step_sources(self, user_input=None):
        """Config flow step for when sources has been selected."""

        return self.async_create_entry(title="SIA Module", data=user_input,)

    async def get_sensor_info(self, sia_url: str, username: str, password: str):
        """Gets sensor info from SIA"""

        auth = BasicAuth(username, password=password)
        url = f"http://{sia_url}/api/init"

        async with ClientSession(auth=auth) as session:
            async with session.get(url) as resp:
                json = await resp.json()

        sensors = []

        for plugin in json["plugins"]:
            plugin_name = plugin["name"]

            for device in plugin["devices"]:
                device_id = device["id"]

                for item in device["items"]:
                    sensors.append(
                        {
                            "id": item["id"],
                            "plugin": plugin_name,
                            "device_id": device_id,
                            "unit": item["unit"],
                            "name": item["name"],
                        }
                    )
        return sensors
