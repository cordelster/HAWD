import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from .const import DOMAIN

CONF_RADIUS = "radius_km"
CONF_MIN_SEVERITY = "min_severity"
CONF_INCLUDE_ORDERS = "include_orders"
CONF_INCLUDE_WARNINGS = "include_warnings"
CONF_INCLUDE_ADVISORIES = "include_advisories"
CONF_ZONES = "zones"

ZONE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_LATITUDE): vol.Coerce(float),
        vol.Required(CONF_LONGITUDE): vol.Coerce(float),
        vol.Optional(CONF_RADIUS, default=25): vol.Coerce(float),
        vol.Optional(CONF_MIN_SEVERITY, default=0): vol.Coerce(float),
        vol.Optional(CONF_INCLUDE_ORDERS, default=True): bool,
        vol.Optional(CONF_INCLUDE_WARNINGS, default=True): bool,
        vol.Optional(CONF_INCLUDE_ADVISORIES, default=False): bool,
    }
)

class WatchDutyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="WatchDuty", data={}, options={CONF_ZONES: [user_input]})

        return self.async_show_form(
            step_id="user",
            data_schema=ZONE_SCHEMA,
            description_placeholders={"example": "Add a zone for monitoring fires."},
        )

    async def async_step_options(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Options", data=user_input)

        # For simplicity, just show a single zone config form — UI editing of multiple zones could use selector UI
        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema({
                vol.Required(CONF_ZONES, default=[]): vol.All([ZONE_SCHEMA]),
            }),
        )
