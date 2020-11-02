const locationNameSelector = '#main-content > div:nth-child(2) > span > span:nth-child(1) > div > div > div > h2';
const checkAddressExists = '.store-address';
const streetAddressSelector = '.store-address > span:nth-child(1)';
const citySelector = '#main-content > div:nth-child(2) > span > span:nth-child(3) > div.salon-detail-wrap > div > div > div > div > div.salon-address.loc-details-edit > div.salon-address > span:nth-child(3) > span > span:nth-child(3)';
const stateSelector = '#main-content > div:nth-child(2) > span > span:nth-child(3) > div.salon-detail-wrap > div > div > div > div > div.salon-address.loc-details-edit > div.salon-address > span:nth-child(3) > span > span:nth-child(4)';
const zipSelector = '#main-content > div:nth-child(2) > span > span:nth-child(3) > div.salon-detail-wrap > div > div > div > div > div.salon-address.loc-details-edit > div.salon-address > span:nth-child(3) > span > span:nth-child(5)';
const phoneSelector = '#sdp-phone';
const latitudeSelector = '#main-content > div:nth-child(2) > span > span:nth-child(3) > div.salon-detail-wrap > div > div > div > div > div:nth-child(8) > meta:nth-child(1)';
const longitudeSelector = '#main-content > div:nth-child(2) > span > span:nth-child(3) > div.salon-detail-wrap > div > div > div > div > div:nth-child(8) > meta:nth-child(2)';
const hourSelector = '#main-content > div:nth-child(2) > span > span:nth-child(3) > div.salon-detail-wrap > div > div > div > div > div.salon-timings';

module.exports = {
  locationNameSelector,
  checkAddressExists,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hourSelector,
};
