import aiohttp
import async_timeout
import logging

BASE_URL = "https://api.watchduty.org/api/v1"

_LOGGER = logging.getLogger(__name__)

class WatchDutyAPI:
    def __init__(self, session: aiohttp.ClientSession = None):
        self.session = session or aiohttp.ClientSession()

    async def fetch_active_incidents(self):
        url = f"{BASE_URL}/geo_events?is_active=true"
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            _LOGGER.error("Failed to fetch active incidents: %s", e)
            raise

    async def fetch_incident_reports(self, geo_event_id: int, *, moderated=True, active=True, has_lat_lng=True):
        url = f"{BASE_URL}/reports/?geo_event_id={geo_event_id}"
        url += f"&is_moderated={str(moderated).lower()}"
        url += f"&is_active={str(active).lower()}"
        url += f"&has_lat_lng={str(has_lat_lng).lower()}"

        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            _LOGGER.error("Failed to fetch reports for geo_event_id=%s: %s", geo_event_id, e)
            raise

    async def close(self):
        await self.session.close()
