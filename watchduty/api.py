import aiohttp

BASE_URL = "https://api.watchduty.org/api/v1"

async def fetch_active_incidents(session):
    url = f"{BASE_URL}/geo_events?is_active=true"
    async with session.get(url) as resp:
        return await resp.json()

async def fetch_reports(session, event_id):
    url = f"{BASE_URL}/reports/?geo_event_id={event_id}&is_moderated=true&is_active=true&has_lat_lng=true"
    async with session.get(url) as resp:
        return await resp.json()