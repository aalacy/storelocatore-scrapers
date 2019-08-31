const locationNameSelector = 'header > div.overlay > div.title > h1';
const streetAddressSelector = 'span[itemprop="streetAddress"]';
const citySelector = 'span[itemprop="addressLocality"]';
const stateSelector = 'span[itemprop="addressRegion"]';
const zipSelector = 'span[itemprop="postalCode"]';
const phoneSelector = 'span[itemprop="telephone"]';
const addressBlockSelector = 'div.info > address';

module.exports = {
  locationNameSelector,
  addressBlockSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
};
