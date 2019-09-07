const locationExistsSelector = 'body > div.wrapper > div > div > div.container > div.conversion-section.clearfix > div > div.jiffylube-location.pull-left > div > div.location > div:nth-child(3) > a';
const locationNameSelector = 'body > div.wrapper > div > div > div.container > div.conversion-section.clearfix > div > div.jiffylube-location.pull-left > div > div.location > div:nth-child(1) > a';
const locationNumberSelector = 'body > div.wrapper > div > div > div.container > div.conversion-section.clearfix > div > div.jiffylube-location.pull-left > div > div.location > div:nth-child(1) > a > span';
const addressLine1Selector = 'body > div.wrapper > div > div > div.container > div.conversion-section.clearfix > div > div.jiffylube-location.pull-left > div > div.location > div:nth-child(3) > a > span.myJLAddressLine1.location-address';
const addressLine2Selector = 'body > div.wrapper > div > div > div.container > div.conversion-section.clearfix > div > div.jiffylube-location.pull-left > div > div.location > div:nth-child(3) > a > span.myJLCityState.location-city--state';
const phoneSelector = 'body > div.wrapper > div > div > div.container > div.conversion-section.clearfix > div > div.jiffylube-location.pull-left > div > div.location > div.location-phone > span';
const bingMapsUrlSelector = '#storeMapDiv > div > div:nth-child(2) > div.bm_bottomLeftOverlay > div > a';
const hourSelector = '#myJLDays';

module.exports = {
  locationExistsSelector,
  locationNameSelector,
  locationNumberSelector,
  addressLine1Selector,
  addressLine2Selector,
  phoneSelector,
  bingMapsUrlSelector,
  hourSelector,
};
