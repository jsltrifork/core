from homeassistant import config_entries
from .const import DOMAIN
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

CONF_URL = "url"
CONF_SOURCES = "sources"
CONF_DEVICE_ID = "deviceId"
CONF_PLUGIN = "plugin"
CONF_ITEM_ID = "itemId"

SOURCE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PLUGIN): cv.string,
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Required(CONF_ITEM_ID): cv.string,
    }
)

SIA_SCHEMA = {
    vol.Required(CONF_URL): str,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
}


class SIAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    VERSION = 1

    data = None
    has_sources = True

    async def async_step_user(self, user_input=None):
        if not user_input:
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema(SIA_SCHEMA)
            )

        if not self.has_sources:
            self.has_sources = True
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema({vol.Required(CONF_URL): str})
            )
        _LOGGER.info(user_input)

        return self.async_create_entry(
            title="This is a title",
            description="This is a description",
            data=user_input,
        )
