DOMAIN = "watchduty"

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .api import WatchDutyAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the WatchDuty component from configuration.yaml (if used)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WatchDuty from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api = WatchDutyAPI()
    coordinator = WatchDutyDataCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class WatchDutyDataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: WatchDutyAPI):
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name="WatchDuty Fire Incident Data",
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self):
        try:
            return await self.api.fetch_active_incidents()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with WatchDuty API: {err}")
