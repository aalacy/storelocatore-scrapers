const locationNameSelector = '.title-wrap > h2';
const streetAddressSelector = 'li[itemprop="streetAddress"]';
const citySelector = 'span[itemprop="addressLocality"]';
const stateSelector = 'span[itemprop="addressRegion"]';
const zipSelector = 'span[itemprop="postalCode"]';
const phoneSelector = '.phone';
const latitudeSelector = '#location-lat';
const longitudeSelector = '#location-lng';
const hourSelector = '#single-location-wrap > div > div:nth-child(3) > div.col-md-4 > div > div:nth-child(2) > p';

module.exports = {
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hourSelector,
};
