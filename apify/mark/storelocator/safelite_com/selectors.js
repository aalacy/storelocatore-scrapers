const storeExistsSelector = '.ratings';
const addressExistsSelector = 'div.content-block:nth-child(3) > h4:nth-child(1)';
const cityStateSelector = '#MainContent_C001_Col00 > div:nth-child(1) > h1:nth-child(1)'
const addressSelector = 'div.content-block:nth-child(3) > p:nth-child(2)';
const googleMapSelector = '#map-1';

const getScheduleButtonSelector = hasAddress => `#MainContent_C001_Col00 > div:nth-child(3) > p:nth-child(${hasAddress ? 4 : 2}) > a`;
const getHoursSelector = (hasAddress, hasScheduleButton) => `#MainContent_C001_Col00 > div:nth-child(3) > p:nth-child(${hasAddress && hasScheduleButton ? 6 : 4})`
const getPhoneSelector = (hasAddress) => `div.content-block:nth-child(3) > p:nth-child(${hasAddress ? 7 : 5})`;


module.exports = {
  storeExistsSelector,
  addressExistsSelector,
  cityStateSelector,
  addressSelector,
  googleMapSelector,
  getScheduleButtonSelector,
  getPhoneSelector,
  getHoursSelector
};
