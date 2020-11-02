const locationHrefSelector = 'ul.sub-menu li a';
const locationNameSelector = 'div[itemprop="name"]';
const streetAddressSelector = 'div[itemprop="streetAddress"]';
const citySelector = 'span[itemprop="addressLocality"]';
const stateSelector = 'span[itemprop="addressRegion"]';
const zipSelector = 'span[itemprop="postalCode"]';
const phoneSelector = 'span[itemprop="telephone"]';
const latitudeSelector = 'div[itemprop="geo"] > meta:nth-child(1)';
const longitudeSelector = 'div[itemprop="geo"] > meta:nth-child(2)';
const hourSelector = 'meta[itemprop="openingHours"]';

const locationBlock = 'li.g1-column.g1-three-fifth.g1-valign-top > p:nth-child(3)';
const locationNameSelector2 = 'li.g1-column.g1-three-fifth.g1-valign-top > h1 > span';

module.exports = {
  locationHrefSelector,
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hourSelector,
  locationBlock,
  locationNameSelector2,
};
