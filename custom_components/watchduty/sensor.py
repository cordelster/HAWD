from homeassistant.helpers.entity import Entity
from homeassistant.util import location as loc_util
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE, CONF_RADIUS
from .const import *

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    zone_config = entry.data  # Get the zone config from entry.data
    async_add_entities([WatchDutySensor(coordinator, zone_config)], True)  # Pass coordinator and zone_config


class WatchDutySensor(SensorEntity):  # Inherit from SensorEntity
    def __init__(self, coordinator, zone_config):
        self.coordinator = coordinator
        self.zone = zone_config
        self._attr_name = f"WatchDuty - {zone_config[CONF_NAME]}"
        self._attr_unique_id = f"watchduty_{zone_config[CONF_NAME].lower().replace(' ', '_')}"
        self._attr_native_value = 0  # e.g., count of nearby fires

    async def async_update(self):
        # Data is already fetched by coordinator
        data = self.coordinator.data or []

        center_lat = self.zone[CONF_LATITUDE]
        center_lon = self.zone[CONF_LONGITUDE]
        radius = self.zone.get(CONF_RADIUS, DEFAULT_RADIUS)
        min_severity = self.zone.get(CONF_MIN_SEVERITY, DEFAULT_MIN_SEVERITY)

        include_orders = self.zone.get(CONF_INCLUDE_ORDERS, True)
        include_warnings = self.zone.get(CONF_INCLUDE_WARNINGS, True)
        include_advisories = self.zone.get(CONF_INCLUDE_ADVISORIES, False)

        filtered = []

        for fire in data:
            lat = fire.get("latitude")
            lon = fire.get("longitude")
            severity = fire.get("acreage", 0)

            if lat is None or lon is None:
                continue

            distance = loc_util.distance(center_lat, center_lon, lat, lon)
            if distance > radius or severity < min_severity:
                continue

            evacuation_status = "none"
            if fire.get("evacuation_orders"):
                evacuation_status = "order"
            elif fire.get("evacuation_warnings"):
                evacuation_status = "warning"
            elif fire.get("evacuation_advisories"):
                evacuation_status = "advisory"

            if (evacuation_status == "order" and not include_orders) or \
               (evacuation_status == "warning" and not include_warnings) or \
               (evacuation_status == "advisory" and not include_advisories):
                continue

            filtered.append({
                "id": fire.get("id"),
                "name": fire.get("name"),
                "latitude": lat,
                "longitude": lon,
                "acreage": severity,
                "containment": fire.get("containment", 0),
                "evacuation_status": evacuation_status,
                "distance_km": round(distance, 2),
            })

        self._attr_native_value = len(filtered)
        self._attr_extra_state_attributes = {
            "nearby_fires": filtered
        }

    @property
    def native_value(self):
        return len(self.coordinator.data or [])

    @property
    def extra_state_attributes(self):
        return {
            "fires": self.coordinator.data
        }