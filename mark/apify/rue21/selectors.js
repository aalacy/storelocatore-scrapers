const locationInfoExists = '#address';
const locationNameSelector = '#location-name > span.location-geomodifier';
const checkAddressSelector = '#address > span.c-address-street span';
const streetSelector = '#address > span.c-address-street > span.c-address-street-1';
const streetAddress2Selector = '#address > span.c-address-street > span.c-address-street-2';
const citySelector = '#address > span.c-address-city > span:nth-child(1)';
const stateSelector = '#address > abbr.c-address-state';
const zipSelector = '#address > span.c-address-postal-code';
const phoneSelector = '#telephone';
const geoSelector = '#dir-map > div.mapboxgl-canvas-container.mapboxgl-interactive > div';
const hourSelector = '#main > div > div:nth-child(3) > div.col-lg-7.col-md-8 > div:nth-child(3) > div:nth-child(2) > div.c-location-hours > div > table > tbody';


module.exports = {
  locationInfoExists,
  locationNameSelector,
  checkAddressSelector,
  streetSelector,
  streetAddress2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  geoSelector,
  hourSelector,
};
