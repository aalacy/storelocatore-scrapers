const locationNameSelector = '#location-name > span.LocationName-geo';
const checkStoreExists = '#address';
const checkAddress = '#address > span.c-address-street span';
const streetSelector = '.c-address-street-1';
const street2Selector = '.c-address-street-2';
const citySelector = '#address > span.c-address-city.break-before > span:nth-child(1)';
const stateSelector = '#address > abbr.c-address-state';
const zipSelector = '#address > span.c-address-postal-code';
const countryCodeSelector = '#address > abbr.c-address-country-name.c-address-country-us.break-before';
const phoneSelector = '#telephone';
const geoSelector = '#dir-map-desktop > div.mapboxgl-canvas-container > div';
const hourSelector = '#main > div > div:nth-child(4) > section.LocationInfo > div.LocationInfo-hoursInfo > div:nth-child(2) > div > table > tbody';

module.exports = {
  locationNameSelector,
  checkStoreExists,
  checkAddress,
  streetSelector,
  street2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  countryCodeSelector,
  phoneSelector,
  geoSelector,
  hourSelector,
};
