const locationNameSelector = '#main-content > span > div.sdp-template-wrap > span > div > div > div > section > div > div > div > span.store-title.hidden-md.hidden-lg';
const streetAddressSelector = 'span[itemprop="streetAddress"]';
const citySelector = 'span[itemprop="addressLocality"]';
const stateSelector = 'span[itemprop="addressRegion"]';
const zipSelector = 'span[itemprop="postalCode"]';
const phoneSelector = '.sdp-phone';
const latitudeSelector = 'meta[itemprop="latitude"]';
const longitudeSelector = 'meta[itemprop="longitude"]';
const hourSelector = '.sdp-store-hours';

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
