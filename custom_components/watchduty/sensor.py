from homeassistant.helpers.entity import Entity
from homeassistant.util import location as loc_util
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE, CONF_RADIUS
from .const import *
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data[CONF_NAME]
    async_add_entities([WatchDutySensor(coordinator, entry.data)], True)  # Pass entry.data


class WatchDutySensor(SensorEntity):
    def __init__(self, coordinator, zone_config):
        self.coordinator = coordinator
        self.zone = zone_config
        self._attr_name = f"WatchDuty - {zone_config[CONF_NAME]}"
        self._attr_unique_id = f"watchduty_{zone_config[CONF_NAME].lower().replace(' ', '_')}"
        self._attr_native_unit_of_measurement = "fires"  # Or whatever makes sense
        self._attr_native_value = 0
        self._attr_latitude = zone_config[CONF_LATITUDE]  # Center latitude
        self._attr_longitude = zone_config[CONF_LONGITUDE]  # Center longitude

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

        filtered_fires = []
        active_fires = []
        prescribed_burns = 0
        contained_fires = 0
        max_fire_acreage = 0
        in_evacuation_order = False
        evacuation_orders = []
        closest_fire_distance = float('inf')  # Initialize to infinity

        for fire in data:
            lat = fire.get("latitude")
            lon = fire.get("longitude")
            severity = fire.get("acreage", 0)

            if lat is None or lon is None:
                continue

            distance = loc_util.distance(center_lat, center_lon, lat, lon)

            if distance > radius or severity < min_severity:
                continue

            # Update closest fire distance
            closest_fire_distance = min(closest_fire_distance, distance)

            evacuation_status = "none"
            if fire.get("evacuation_orders"):
                evacuation_status = "order"
                in_evacuation_order = True
                evacuation_orders.append(fire.get("id"))  # Store the fire ID
            elif fire.get("evacuation_warnings"):
                evacuation_status = "warning"
            elif fire.get("evacuation_advisories"):
                evacuation_status = "advisory"

            if (evacuation_status == "order" and not include_orders) or (
                evacuation_status == "warning" and not include_warnings
            ) or (evacuation_status == "advisory" and not include_advisories):
                continue

            fire_data = {
                "id": fire.get("id"),
                "name": fire.get("name"),
                "latitude": lat,
                "longitude": lon,
                "acreage": severity,
                "containment": fire.get("containment", 0),
                "evacuation_status": evacuation_status,
                "distance_km": round(distance, 2),
                "geo_event_type": fire.get("geo_event_type"),
                "is_prescribed": fire.get("is_prescribed", False),
                "has_custom_evacuation_orders": fire.get("has_custom_evacuation_orders", False),
                "has_custom_evacuation_warnings": fire.get("has_custom_evacuation_warnings", False),
                "has_custom_evacuation_advisories": fire.get("has_custom_evacuation_advisories", False),
            }

            filtered_fires.append(fire_data)

            if fire_data["geo_event_type"] == "fire":
                if fire_data["is_prescribed"]:
                    prescribed_burns += 1
                else:
                    active_fires.append(fire_data["id"])
                    max_fire_acreage = max(max_fire_acreage, fire_data["acreage"])
                if fire_data["containment"] == 100:  # Assuming 100% containment means contained
                    contained_fires += 1

        self._attr_native_value = len(filtered_fires)
        self._attr_extra_state_attributes = {
            "nearby_fires": filtered_fires,
            "fire_count": len(filtered_fires),
            "closest_fire_distance": round(closest_fire_distance, 2) if closest_fire_distance != float('inf') else None,
            "in_evacuation_order": in_evacuation_order,
            "evacuation_orders": evacuation_orders,
            "active_fires": active_fires,
            "prescribed_burns": prescribed_burns,
            "contained_fires": contained_fires,
            "max_fire_acreage": max_fire_acreage,
        }

    @property
    def native_value(self):
        return len(self.coordinator.data or [])

    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes