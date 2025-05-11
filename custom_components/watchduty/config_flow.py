from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from .const import DOMAIN

STEP_USER = "user"
STEP_ZONE = "zone"
STEP_MANUAL = "manual"

class WatchDutyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            use_zone = user_input["use_zone"]
            return await self.async_step_zone() if use_zone else await self.async_step_manual()

        return self.async_show_form(
            step_id=STEP_USER,
            data_schema=vol.Schema({
                vol.Required("use_zone", default=True): bool,
            }),
        )

    async def async_step_zone(self, user_input=None):
        zones = {
            state.entity_id: state.attributes.get("friendly_name", state.name)
            for state in self.hass.states.async_all("zone")
        }

        if user_input is not None:
            zone_entity = user_input["zone"]
            zone = self.hass.states.get(zone_entity)
            lat = zone.attributes["latitude"]
            lon = zone.attributes["longitude"]
            return self.async_create_entry(title=zone.name, data={
                CONF_NAME: zone.name,
                CONF_LATITUDE: lat,
                CONF_LONGITUDE: lon,
                "radius": user_input["radius"],
                "min_severity": user_input["min_severity"],
                "include_orders": user_input["include_orders"],
                "include_warnings": user_input["include_warnings"],
                "include_advisories": user_input["include_advisories"],
            })

        return self.async_show_form(
#            step_id="user",
            step_id=STEP_ZONE,
            data_schema=vol.Schema({
                vol.Required("zone"): vol.In(zones),
                vol.Required("radius", default=25): int,
                vol.Optional("min_severity", default=0): int,
                vol.Optional("include_orders", default=True): bool,
                vol.Optional("include_warnings", default=True): bool,
                vol.Optional("include_advisories", default=False): bool,
            }),
        )

    async def async_step_manual(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data={
                CONF_NAME: user_input["name"],
                CONF_LATITUDE: user_input["latitude"],
                CONF_LONGITUDE: user_input["longitude"],
                "radius": user_input["radius"],
                "min_severity": user_input["min_severity"],
                "include_orders": user_input["include_orders"],
                "include_warnings": user_input["include_warnings"],
                "include_advisories": user_input["include_advisories"],
            })

        return self.async_show_form(
            step_id=STEP_MANUAL,
            data_schema=vol.Schema({
                vol.Required("name", default="Manual Location"): str,
                vol.Required("latitude"): float,
                vol.Required("longitude"): float,
                vol.Required("radius", default=25): int,
                vol.Optional("min_severity", default=0): int,
                vol.Optional("include_orders", default=True): bool,
                vol.Optional("include_warnings", default=True): bool,
                vol.Optional("include_advisories", default=False): bool,
            }),
        )
