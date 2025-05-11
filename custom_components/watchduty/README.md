# WatchDuty Wildfire Alerts for Home Assistant

This custom component tracks wildfire alerts via [WatchDuty](https://www.watchduty.org) and shows them as sensors and on a map in Lovelace.

## Installation

1. Place `watchduty/` in `custom_components/`
2. Restart Home Assistant

## YAML Configuration

```yaml
watchduty:
  zones:
    - name: Home
      latitude: 38.123
      longitude: -122.456
      radius: 25
      min_severity: 10
      include_orders: true
      include_warnings: true
      include_advisories: false
```

## Lovelace Map Card

```yaml
type: custom:watchduty-map-card
zoom_to_fit: true
```