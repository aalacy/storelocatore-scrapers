const locationInfoExists = '#address';
const locationNameSelector = '#location-name > span.location-name-geo';
const checkAddressSelector = '#address div';
const streetSelector = '#address > div:nth-child(2) > span';
const streetAddress2Selector = '#address > div:nth-child(3) > span';
const citySelector = '.c-address-city';
const stateSelector = '.c-address-state';
const zipSelector = '.c-address-postal-code';
const countrySelector = '#address';
const phoneSelector = '#telephone';
const geoSelector = '#dir-map > div.mapboxgl-canvas-container > div';
const hourSelector = '#main > div > header > div > div.c-location-hours > div > table > tbody';

module.exports = {
  locationInfoExists,
  locationNameSelector,
  checkAddressSelector,
  streetSelector,
  streetAddress2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  countrySelector,
  phoneSelector,
  geoSelector,
  hourSelector,
};
