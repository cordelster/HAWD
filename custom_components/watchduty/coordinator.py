from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
import aiohttp
from .api import fetch_active_incidents

_LOGGER = logging.getLogger(__name__)

class WatchDutyDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config):
        self.config = config
        self.session = aiohttp.ClientSession()
        super().__init__(
            hass,
            _LOGGER,
            name="WatchDuty Data Coordinator",
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        return await fetch_active_incidents(self.session)