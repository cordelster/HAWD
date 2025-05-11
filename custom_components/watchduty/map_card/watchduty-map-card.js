class WatchDutyMapCard extends HTMLElement {
  set hass(hass) {
    const config = this._config;
    const entities = config.entities || [];
    if (!this._map) return;

    // Clear old markers
    if (this._markers) {
      this._markers.forEach(m => m.remove());
    }

    this._markers = [];

    for (const entityId of entities) {
      const stateObj = hass.states[entityId];
      if (!stateObj || !stateObj.attributes.nearby_fires) continue;

      const fires = stateObj.attributes.nearby_fires;
      for (const fire of fires) {
        const marker = L.marker([fire.latitude, fire.longitude])
          .addTo(this._map)
          .bindPopup(`
            <strong>${fire.name}</strong><br>
            🔥 ${fire.acreage} acres<br>
            🧯 ${fire.containment}% contained<br>
            🚨 Evacuation: ${fire.evacuation_status || "n/a"}<br>
            <a href="https://api.watchduty.org/api/v1/geo_events/${fire.id}" target="_blank">View Report</a>
          `);
        this._markers.push(marker);
      }
    }
  }

  setConfig(config) {
    if (!config.entities || !Array.isArray(config.entities)) {
      throw new Error("You must define at least one entity.");
    }

    this._config = config;

    this.innerHTML = `
      <style>
        #map { height: 100%; width: 100%; }
      </style>
      <div id="map"></div>
    `;
  }

  async connectedCallback() {
    if (!window.L) {
      await this._loadLeaflet();
    }
    this._initializeMap();
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
    this._map = L.map(this.querySelector("#map")).setView([37.7749, -122.4194], 6);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors"
    }).addTo(this._map);
  }

  getCardSize() {
    return 6;
  }
}

customElements.define("watchduty-map-card", WatchDutyMapCard);

