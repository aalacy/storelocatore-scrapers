const locationExistsSelector = 'meta[itemprop="hasMap"]';
const locationNameSelector = 'meta[itemprop="name"]';
const streetAddressSelector = 'span[itemprop="streetAddress"]';
const citySelector = 'span[itemprop="addressLocality"]';
const stateSelector = 'span[itemprop="addressRegion"]';
const zipSelector = 'span[itemprop="postalCode"]';
const phoneSelector = '.phone-link > span';
const latitudeSelector = 'meta[itemprop="latitude"]';
const longitudeSelector = 'meta[itemprop="longitude"]';
const geoUrlSelector = '#LocalFooterSocial > ul > li:nth-child(2) > a[itemprop="sameAs"]';

module.exports = {
  locationExistsSelector,
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  geoUrlSelector,
};
