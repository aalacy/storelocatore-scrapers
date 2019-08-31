const locationNameSelector = 'body > main > div > div > article > section > header > h1';
const addressSelector = 'body > main > div > div > article > section > header > address > span:nth-child(1)';
const citySelector = 'body > main > div > div > article > section > header > address > span:nth-child(3)';
const stateSelector = 'body > main > div > div > article > section > header > address > span:nth-child(4)';
const zipCodeSelector = 'body > main > div > div > article > section > header > address > span:nth-child(5)';
const phoneSelector = '#office-number > span';
const latitudeSelector = 'body > main > div > div > article > section > header > div > meta:nth-child(1)';
const longitudeSelector = 'body > main > div > div > article > section > header > div > meta:nth-child(2)';
const hourSelector = '#collapseOfficeHours > div > div';

module.exports = {
  locationNameSelector,
  addressSelector,
  citySelector,
  stateSelector,
  zipCodeSelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hourSelector,
};
