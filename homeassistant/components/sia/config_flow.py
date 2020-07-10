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

        sources_data = await self._get_init_info(url, username, password)

        _LOGGER.info(sources_data)

        return self.async_show_form(
            step_id="sources", data_schema=vol.Schema({vol.Required(CONF_URL,): bool}),
        )

    async def async_step_sources(self, user_input=None):
        """Config flow step for when sources has been selected."""

        return self.async_create_entry(title="SIA Module", data=user_input,)

    async def _get_init_info(self, sia_url: str, username: str, password: str):
        auth = BasicAuth(username, password=password)
        url = f"http://{sia_url}/api/init"

        async with ClientSession(auth=auth) as session:
            async with session.get(url) as resp:
                return await resp.json()
