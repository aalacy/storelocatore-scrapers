const locationNameSelector = '#location-name > span.location-title-geomodifier';
const storeNumberSelector = '#location-info > div > div:nth-child(1) > div.location-info-code';
const checkStoreExists = '#address > address';
const checkAddress = '#address > address > span.c-address-street span';
const streetSelector = '#address > address > span.c-address-street > span.c-address-street-1';
const street2Selector = '#address > address > span.c-address-street > span.c-address-street-2';
const citySelector = '#address > address > span.c-address-city > span:nth-child(1)';
const stateSelector = '#address > address > abbr.c-address-state';
const zipSelector = '#address > address > span.c-address-postal-code';
const phoneSelector = '#telephone';
const geoSelector = '#dir-map > div.mapboxgl-canvas-container.mapboxgl-interactive > div';
const hourSelector = '#location-info > div > div:nth-child(1) > div:nth-child(10) > div > div > table';

module.exports = {
  locationNameSelector,
  storeNumberSelector,
  checkStoreExists,
  checkAddress,
  streetSelector,
  street2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  geoSelector,
  hourSelector,
};
