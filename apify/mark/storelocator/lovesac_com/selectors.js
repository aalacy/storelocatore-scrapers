const locationHrefSelector = 'a.sl-see-details.js-store-details';
const locationNameSelector = 'h1[itemprop="name"]';
const streetAddressSelector = 'span[itemprop="streetAddress"]';
const citySelector = 'span[itemprop="addressLocality"]';
const stateSelector = 'span[itemprop="addressRegion"]';
const zipSelector = 'span[itemprop="postalCode"]';
const phoneSelector = 'span[itemprop="telephone"]';
const geoUrlSelector = '#store-map > div > div:nth-child(2) > div.bm_bottomLeftOverlay > div > a';
const hourSelector = 'time[itemprop="openingHours"]';

module.exports = {
  locationHrefSelector,
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  geoUrlSelector,
  hourSelector,
};
