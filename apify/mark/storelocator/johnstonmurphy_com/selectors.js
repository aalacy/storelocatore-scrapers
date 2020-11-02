// Initial Page Selectors
const storeSelector = '#storegroups > table.store-location-results.retailstores > tbody > tr';
const factorySelector = '#storegroups > table.factorystores.store-location-results > tbody > tr';
const departmentSelector = '#storegroups > table.specialitystores.store-location-results > tbody > tr';

// Detail Page Selectors
const detailStoreName = '#primary > div > div.store-info-container > h1';
const detailAddress = '#primary > div > div > div > span.store-addressLine1';
const detailGeoLocation = '#google-map-store > div > div > div:nth-child(3) > a';

module.exports = {
  storeSelector,
  factorySelector,
  departmentSelector,
  detailStoreName,
  detailAddress,
  detailGeoLocation,
};
