const locationExistsSelector = '#PublicWrapper > div > div > div > div:nth-child(2) > div > h3:nth-child(1)';
const locationNameSelector = '#PublicWrapper > div > div > div.store-content > div:nth-child(1) > div.col-md-5 > h1';
const streetAddressSelector = '#PublicWrapper > div > div > div.store-content > div:nth-child(2) > div > span:nth-child(2)';
const cityStateZipSelector = '#PublicWrapper > div > div > div.store-content > div:nth-child(2) > div > span:nth-child(4)';
const phoneSelector = '#PublicWrapper > div > div > div.store-content > div:nth-child(2) > div > a:nth-child(6)';
const hoursExistsSelector = '#PublicWrapper > div > div > div.store-content > div:nth-child(2) > div > h3:nth-child(8)';
const hourSelector = '#PublicWrapper > div > div.container.container-content > div.store-content > div:nth-child(2) > div > table';
const googleMapsUrlSelector = '#map_canvas > div > div > div:nth-child(3) > a';

module.exports = {
  locationExistsSelector,
  locationNameSelector,
  streetAddressSelector,
  cityStateZipSelector,
  phoneSelector,
  hoursExistsSelector,
  hourSelector,
  googleMapsUrlSelector,
};
