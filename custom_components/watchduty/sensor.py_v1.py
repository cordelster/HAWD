import logging
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN
from .coordinator import WatchDutyDataCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistantType, config_entry, async_add_entities):
    coordinator: WatchDutyDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Example multiple sensors (user-configurable later)
    zones = [
        {
            "name": "Home Zone",
            "latitude": 38.0,
            "longitude": -122.4,
            "radius_km": 25,
            "min_severity": 0,
            "include_orders": True,
            "include_warnings": True,
            "include_advisories": False
        },
        {
            "name": "Cabin Zone",
            "latitude": 39.2,
            "longitude": -121.6,
            "radius_km": 50,
            "min_severity": 10,
            "include_orders": True,
            "include_warnings": True,
            "include_advisories": True
        }
    ]

    sensors = [
        WatchDutyFireSensor(
            coordinator,
            name=zone["name"],
            latitude=zone["latitude"],
            longitude=zone["longitude"],
            radius_km=zone["radius_km"],
            min_severity=zone["min_severity"],
            include_orders=zone["include_orders"],
            include_warnings=zone["include_warnings"],
            include_advisories=zone["include_advisories"]
        )
        for zone in zones
    ]

    async_add_entities(sensors, update_before_add=True)

class WatchDutyFireSensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: WatchDutyDataCoordinator,
        name: str,
        latitude: float,
        longitude: float,
        radius_km: float,
        min_severity: float = 0,
        include_orders: bool = True,
        include_warnings: bool = True,
        include_advisories: bool = True
    ):
        super().__init__(coordinator)
        self._attr_name = name
        self.latitude = latitude
        self.longitude = longitude
        self.radius_km = radius_km
        self.min_severity = min_severity
        self.include_orders = include_orders
        self.include_warnings = include_warnings
        self.include_advisories = include_advisories
        self._attr_native_value = STATE_UNKNOWN
        self._attr_extra_state_attributes = {}

    @staticmethod
    def _calculate_distance_km(lat1, lon1, lat2, lon2):
        from math import radians, cos, sin, asin, sqrt
        R = 6371  # Earth radius in km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return R * c

    def _passes_filters(self, event):
        acreage = event.get("acreage", 0.0)
        if acreage < self.min_severity:
            return False

        has_order = bool(event.get("evacuation_orders"))
        has_warning = bool(event.get("evacuation_warnings"))
        has_advisory = bool(event.get("evacuation_advisories"))

        if has_order and self.include_orders:
            return True
        if has_warning and self.include_warnings:
            return True
        if has_advisory and self.include_advisories:
            return True

        # If none of the above, still pass if no evac filter is enabled
        return not (self.include_orders or self.include_warnings or self.include_advisories)

    def _filter_fires_by_radius(self, incidents):
        nearby = []
        for event in incidents:
            lat = event.get("lat")
            lon = event.get("lng")
            if lat is not None and lon is not None:
                dist = self._calculate_distance_km(self.latitude, self.longitude, lat, lon)
                if dist <= self.radius_km and self._passes_filters(event):
                    event["distance_km"] = round(dist, 2)
                    nearby.append(event)
        return nearby

    def _get_highest_alert_level(self, incident):
        if incident.get("evacuation_orders"):
            return "order"
        if incident.get("evacuation_warnings"):
            return "warning"
        if incident.get("evacuation_advisories"):
            return "advisory"
        return "none"

    def _build_attributes(self, filtered):
        return {
            "nearby_fires": len(filtered),
            "fires": [
                {
                    "id": fire["id"],
                    "name": fire.get("name"),
                    "type": fire.get("geo_event_type"),
                    "acreage": fire.get("acreage"),
                    "containment": fire.get("containment"),
                    "alert_level": self._get_highest_alert_level(fire),
                    "distance_km": fire["distance_km"],
                }
                for fire in filtered
            ]
        }

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes

    async def async_update(self):
        await self.coordinator.async_request_refresh()
        incidents = self.coordinator.data or []
        filtered = self._filter_fires_by_radius(incidents)
        self._attr_native_value = f"{len(filtered)} nearby fire(s)"
        self._attr_extra_state_attributes = self._build_attributes(filtered)
