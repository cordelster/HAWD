class WatchDutyMapCard extends HTMLElement {
  static get properties() {
    return {
      _config: { type: Object },
      _hass: { type: Object },
    };
  }

  constructor() {
    super();
    this._map = null;
    this._markers = [];
    this._mapProvider = 'openstreetmap'; // Default map provider
  }

  setConfig(config) {
    this._config = config;
    this._mapProvider = config.map_provider || 'openstreetmap'; // Get map provider from config
    this.innerHTML = `
      <style>
        map {
          height: 100%;
          width: 100%;
        }
      </style>
      <div id="map"></div>
    `;
  }

  async connectedCallback() {
    if (!window.L) {
      await this._loadLeaflet();
    }
    this._initializeMap();
    this._updateMarkers();
  }

  async _loadLeaflet() {
    await Promise.all([
      this._loadCSS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"),
      this._loadJS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"),
    ]);
  }

  _loadJS(src) {
    return new Promise(resolve => {
      const el = document.createElement("script");
      el.src = src;
      el.onload = resolve;
      document.head.appendChild(el);
    });
  }

  _loadCSS(href) {
    return new Promise(resolve => {
      const el = document.createElement("link");
      el.rel = "stylesheet";
      el.href = href;
      el.onload = resolve;
      document.head.appendChild(el);
    });
  }

  _initializeMap() {
    if (this._map) {
      this._map.remove(); // Remove existing map if re-initializing
    }
    const mapElement = this.querySelector("#map");
    this._map = L.map(mapElement).setView([37.7749, -122.4194], 6);

    let tileLayer;
    switch (this._mapProvider) {
      case 'openstreetmap':
        tileLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "&copy; OpenStreetMap contributors"
        });
        break;
      // Add other map providers here if you implement them
      // case 'googlemaps':
      //   tileLayer = L.tileLayer('http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
      //     maxZoom: 20,
      //     subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
      //     attribution: 'Map data ©2023 Google'
      //   });
      //   break;
      default:
        tileLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "&copy; OpenStreetMap contributors"
        });
        break;
    }
    tileLayer.addTo(this._map);
  }

  _updateMarkers() {
    if (!this._hass || !this._config.entities) {
      return;
    }

    const entities = this._config.entities;
    const bounds = [];

    // Clear existing markers
    this._markers.forEach(marker => marker.remove());
    this._markers = [];

    for (const entityId of entities) {
      const stateObj = this._hass.states[entityId];
      if (!stateObj?.attributes?.nearby_fires) continue;

      const fires = stateObj.attributes.nearby_fires;
      for (const fire of fires) {
        let markerColor = 'red'; // Default to red for fire
        if (fire.geo_event_type === 'fire' && fire.is_prescribed) {
          markerColor = 'green'; // Green for prescribed burn
        } else if (fire.containment === 100) {
          markerColor = 'gray'; // Gray for contained
        }

        const icon = L.divIcon({
          className: `fire-marker ${markerColor}`,
          html: `<svg viewBox="0 0 24 24" width="24" height="24" fill="${markerColor}"><path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3l.71-.71L12 2zm0 14l-3-3h6l-3 3z"/></svg>`,
          iconSize: [24, 24],
          iconAnchor: [12, 24],
          popupAnchor: [0, -24],
        });

        const marker = L.marker([fire.latitude, fire.longitude], { icon: icon })
          .addTo(this._map)
          .bindPopup(`
            <strong>${fire.name}</strong><br>
            🔥 ${fire.acreage || 'n/a'} acres<br>
            🧯 ${fire.containment !== undefined ? fire.containment + '%' : 'n/a'} contained<br>
            🚨 Evacuation: ${fire.evacuation_status || 'n/a'}<br>
            Type: ${fire.geo_event_type || 'n/a'}<br>
            Prescribed: ${fire.is_prescribed ? 'Yes' : 'No'}<br>
            <a href="https://api.watchduty.org/api/v1/geo_events/${fire.id}" target="_blank">View Report</a>
          `);

        this._markers.push(marker);
        bounds.push([fire.latitude, fire.longitude]);
      }
    }

    if (this._config.zoom_to_fit && bounds.length > 0) {
      this._map.fitBounds(bounds, { padding: [20, 20] });
    }
  }

  set hass(hass) {
    this._hass = hass;
    this._updateMarkers();
  }

  getCardSize() {
    return 6;
  }

  static getStubConfig() {
    return {
      entities: ["sensor.watchduty"],
      zoom_to_fit: true,
      map_provider: "openstreetmap", // Default value in stub
    };
  }

  static getCardEditorContribution() {
    return {
      type: "struct",
      name: "WatchDuty Map Card Configuration",
      schema: {
        entities: {
          type: "array",
          name: "Entities",
          description: "Select your WatchDuty sensor entity.",
          schema: {
            type: "string",
          },
        },
        zoom_to_fit: {
          type: "boolean",
          name: "Zoom to Fit",
          description: "Automatically zoom the map to fit all markers.",
        },
        map_provider: {
          type: "dropdown",
          name: "Map Provider",
          description: "Select the map provider.",
          options: [
            ["openstreetmap", "OpenStreetMap"],
            // ["googlemaps", "Google Maps (API Key required)"],
            // Add other options if you implement them
          ],
        },
      },
    };
  }
}

customElements.define("watchduty-map-card", WatchDutyMapCard);