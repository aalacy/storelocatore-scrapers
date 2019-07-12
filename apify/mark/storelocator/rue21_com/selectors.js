const locationInfoExists = '#address';
const locationNameSelector = '#location-name > span.location-geomodifier';
const streetAddress1Selector = '.c-address-street-1';
const streetAddress2Selector = '.c-address-street-2';
const citySelector = 'span[itemprop="addressLocality"]';
const stateSelector = 'abbr[itemprop="addressRegion"]';
const zipSelector = 'span[itemprop="postalCode"]';
const countrySelector = 'abbr[itemprop="addressCountry"]';
const phoneSelector = 'span[itemprop="telephone"]';
const latitudeSelector = 'meta[itemprop="latitude"]';
const longitudeSelector = 'meta[itemprop="longitude"]';
const hourSelector = '.c-location-hours-details';

module.exports = {
  locationInfoExists,
  locationNameSelector,
  streetAddress1Selector,
  streetAddress2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  countrySelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hourSelector,
};
