const locationInfoExists = '#location-info > div > div.location-info-hero-row > div > div > div.location-info-details > div.location-info-contactInfo > address';
const locationNameSelector = '#location-name > span';
const checkAddressSelector = '#location-info > div > div.location-info-hero-row > div > div > div.location-info-details > div.location-info-contactInfo > address > span.c-address-street span';
const streetSelector = '#location-info > div > div.location-info-hero-row > div > div > div.location-info-details > div.location-info-contactInfo > address > span.c-address-street > span.c-address-street-1';
const streetAddress2Selector = '#location-info > div > div.location-info-hero-row > div > div > div.location-info-details > div.location-info-contactInfo > address > span.c-address-street > span.c-address-street-2';
const citySelector = '#location-info > div > div.location-info-hero-row > div > div > div.location-info-details > div.location-info-contactInfo > address > span.c-address-city > span:nth-child(1)';
const stateSelector = '#location-info > div > div.location-info-hero-row > div > div > div.location-info-details > div.location-info-contactInfo > address > abbr.c-address-state';
const zipSelector = '#location-info > div > div.location-info-hero-row > div > div > div.location-info-details > div.location-info-contactInfo > address > span.c-address-postal-code';
const phoneSelector = '#telephone';
const hourSelector = '#location-info-hours-collapse > div > div > table';

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
  hourSelector,
};
