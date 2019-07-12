const locationNameSelector = 'span.location-title-geomodifier';
const storeNumberSelector = 'div.location-info-code';
const streetSelector = 'span.c-address-street-1';
const street2Selector = 'span.c-address-street-2';
const citySelector = 'span[itemprop="addressLocality"]';
const stateSelector = 'abbr[itemprop="addressRegion"]';
const zipSelector = 'span[itemprop="postalCode"]';
const countrySelector = 'abbr[itemprop="addressCountry"]';
const phoneSelector = '#telephone';
const latitudeSelector = 'meta[itemprop="latitude"]';
const longitudeSelector = 'meta[itemprop="longitude"]';
const hourSelector = '.c-location-hours-details';

module.exports = {
  locationNameSelector,
  storeNumberSelector,
  streetSelector,
  street2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  countrySelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hourSelector,
};
