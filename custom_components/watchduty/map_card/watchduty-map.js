class WatchDutyMapCard extends HTMLElement {
  setConfig(config) {
    this.innerHTML = '<ha-card header="WatchDuty Map"><div>Map will go here.</div></ha-card>';
  }

  getCardSize() {
    return 3;
  }
}
customElements.define('watchduty-map-card', WatchDutyMapCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'watchduty-map-card',
  name: 'WatchDuty Map',
  preview: false,
  description: 'Map card to show wildfire alerts'
});