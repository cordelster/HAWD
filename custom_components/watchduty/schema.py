import voluptuous as vol
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME

ZONE_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): str,
    vol.Required(CONF_LATITUDE): float,
    vol.Required(CONF_LONGITUDE): float,
    vol.Optional("radius", default=25): int,
    vol.Optional("min_severity", default=0): int,
    vol.Optional("include_orders", default=True): bool,
    vol.Optional("include_warnings", default=True): bool,
    vol.Optional("include_advisories", default=False): bool,
})

CONFIG_SCHEMA = vol.Schema({
    "zones": [ZONE_SCHEMA]
})