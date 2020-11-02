const locationNameSelector = 'body > section.section.section--intro.store > div > div > h1';
const streetAddressSelector = 'span[itemprop="street-address"]';
const citySelector = 'span[itemprop="locality"]';
const stateSelector = 'span[itemprop="region"]';
const zipSelector = 'span[itemprop="postal-code"]';
const phoneSelector = '.ga-telephone';
const geoSelector = '#kng-map';
const hourSelector = 'body > section.section.section--store-details.store > div > div > div:nth-child(2)';

module.exports = {
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  geoSelector,
  hourSelector,
};
