from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data[CONF_NAME]
    async_add_entities([WatchDutySensor(name, coordinator)], True)

class WatchDutySensor(SensorEntity):
    def __init__(self, name, coordinator):
        self._attr_name = name
        self.coordinator = coordinator

    @property
    def native_value(self):
        return len(self.coordinator.data or [])

    @property
    def extra_state_attributes(self):
        return {
            "fires": self.coordinator.data
        }

    self._attr_extra_state_attributes = {
      "nearby_fires": filtered_fires
    }

    async def async_update(self):
        await self.coordinator.async_request_refresh()