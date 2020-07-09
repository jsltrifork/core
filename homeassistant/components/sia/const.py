"""Constants for the SIA Module integration."""
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_URL

DOMAIN = "sia"

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
    vol.Required(CONF_URL): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_SOURCES): vol.All(cv.ensure_list, [SOURCE_SCHEMA]),
}
