import voluptuous as vol
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from .const import DOMAIN

CONF_RADIUS = "radius_km"
CONF_MIN_SEVERITY = "min_severity"
CONF_INCLUDE_ORDERS = "include_orders"
CONF_INCLUDE_WARNINGS = "include_warnings"
CONF_INCLUDE_ADVISORIES = "include_advisories"
CONF_ZONES = "zones"

ZONE_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): str,
    vol.Required(CONF_LATITUDE): vol.Coerce(float),
    vol.Required(CONF_LONGITUDE): vol.Coerce(float),
    vol.Optional(CONF_RADIUS, default=25): vol.Coerce(float),
    vol.Optional(CONF_MIN_SEVERITY, default=0): vol.Coerce(float),
    vol.Optional(CONF_INCLUDE_ORDERS, default=True): bool,
    vol.Optional(CONF_INCLUDE_WARNINGS, default=True): bool,
    vol.Optional(CONF_INCLUDE_ADVISORIES, default=False): bool,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_ZONES): vol.All([ZONE_SCHEMA])
    })
}, extra=vol.ALLOW_EXTRA)
