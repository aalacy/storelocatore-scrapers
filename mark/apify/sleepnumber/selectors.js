const locationInfoExists = '#main > div > div:nth-child(1) > div > div.Location-bannerImage > div > div > div.hidden-xs > div:nth-child(1) > div > div.c-location-info';
const locationNameSelector = '#location-name > div.Location-nameGeomodifier';
const checkAddressSelector = '#main > div > div:nth-child(1) > div > div.Location-bannerImage > div > div > div.hidden-xs > div:nth-child(1) > div > div.c-location-info > div.c-location-info-address > address > div.c-AddressRow';
const streetSelector = '#main > div > div:nth-child(1) > div > div.Location-bannerImage > div > div > div.hidden-xs > div:nth-child(1) > div > div.c-location-info > div.c-location-info-address > address > div:nth-child(1) > span';
const streetAddress2Selector = '#main > div > div:nth-child(1) > div > div.Location-bannerImage > div > div > div.hidden-xs > div:nth-child(1) > div > div.c-location-info > div.c-location-info-address > address > div:nth-child(2) > span';
const cityAddress2Selector = '#main > div > div:nth-child(1) > div > div.Location-bannerImage > div > div > div.hidden-xs > div:nth-child(1) > div > div.c-location-info > div.c-location-info-address > address > div:nth-child(3) > span.c-address-city';
const stateAddress2Selector = '#main > div > div:nth-child(1) > div > div.Location-bannerImage > div > div > div.hidden-xs > div:nth-child(1) > div > div.c-location-info > div.c-location-info-address > address > div:nth-child(3) > abbr';
const zipAddress2Selector = '#main > div > div:nth-child(1) > div > div.Location-bannerImage > div > div > div.hidden-xs > div:nth-child(1) > div > div.c-location-info > div.c-location-info-address > address > div:nth-child(3) > span.c-address-postal-code';
const citySelector = '#main > div > div:nth-child(1) > div > div.Location-bannerImage > div > div > div.hidden-xs > div:nth-child(1) > div > div.c-location-info > div.c-location-info-address > address > div:nth-child(2) > span.c-address-city';
const stateSelector = '#main > div > div:nth-child(1) > div > div.Location-bannerImage > div > div > div.hidden-xs > div:nth-child(1) > div > div.c-location-info > div.c-location-info-address > address > div:nth-child(2) > abbr';
const zipSelector = '#main > div > div:nth-child(1) > div > div.Location-bannerImage > div > div > div.hidden-xs > div:nth-child(1) > div > div.c-location-info > div.c-location-info-address > address > div:nth-child(2) > span.c-address-postal-code';
const phoneSelector = '#telephone';
const hourSelector = '#main > div > div:nth-child(1) > div > div.Location-bannerImage > div > div > div.hidden-xs > div:nth-child(3) > div > div > div > table > tbody';
const googleMapsUrlSelector = '#dir-map > div > div > div:nth-child(3) > a';

module.exports = {
  locationInfoExists,
  locationNameSelector,
  checkAddressSelector,
  streetSelector,
  citySelector,
  stateSelector,
  zipSelector,
  streetAddress2Selector,
  cityAddress2Selector,
  stateAddress2Selector,
  zipAddress2Selector,
  phoneSelector,
  googleMapsUrlSelector,
  hourSelector,
};
