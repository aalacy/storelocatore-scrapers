const locationNameSelector = 'body > div.introduction > div > div > div > h1';
const streetAddressSelector = 'span[itemprop="streetAddress"]';
const citySelector = 'span[itemprop="addressLocality"]';
const stateSelector = 'span[itemprop="addressRegion"]';
const addressBlockSelector = 'div[itemprop="address"]';
const phoneSelector = 'span[itemprop="telephone"]';
const geoUrlSelector = 'div[itemprop="address"] > a';
const hourSelector = 'body > div.content.page-content.page-overview > div > div > div.col-xs-12.col-sm-5.side-wrap > div > div > div > div:nth-child(4)';

module.exports = {
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  addressBlockSelector,
  phoneSelector,
  geoUrlSelector,
  hourSelector,
};
