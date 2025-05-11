from homeassistant import config_entries
import voluptuous as vol
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from .const import DOMAIN

class WatchDutyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_LATITUDE): float,
                vol.Required(CONF_LONGITUDE): float,
                vol.Required("radius", default=25): int,
                vol.Optional("min_severity", default=0): int,
                vol.Optional("include_orders", default=True): bool,
                vol.Optional("include_warnings", default=True): bool,
                vol.Optional("include_advisories", default=False): bool,
            })
        )