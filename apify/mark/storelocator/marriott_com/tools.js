const Apify = require('apify');
const _ = require('lodash');
const { Poi } = require('./Poi');

const getLastPage = (array) => {
  const paginationTags = array.map(a => a.replace(/\s/g, '').replace(/\D/g, '')).filter(e => e.length > 0).map(r => parseInt(r, 10));
  return _.max(paginationTags);
};

const formatPhoneNumber = string => string.replace(/\D/g, '');

const removeSpaces = string => string.replace(/\s/g, '');

const countryCodeCheck = (string) => {
  if (string === 'Canada') {
    return 'CA';
  }
  if (string === 'USA') {
    return 'US';
  }
  return undefined;
};

async function pushDetail({ page }) {
  const outerPropertySelector = '.js-property-list-container > div';
  await page.waitForSelector(outerPropertySelector, { waitUntil: 'load', timeout: 0 });
  const dataPropertyOuter = await page.$$eval(outerPropertySelector, de => de
    .map(d => JSON.parse(d.dataset.property)));

  const innerPropertySelector = '.js-property-list-container > div > div > div > div.js-hotel-location > div > div.m-hotel-address';
  await page.waitForSelector(innerPropertySelector, { waitUntil: 'load', timeout: 0 });
  const dataPropertyInner = await page.$$eval(innerPropertySelector, ie => ie.map(i => ({
    address: i.dataset.addressLine1,
    postalCode: i.dataset.postalCode,
    city: i.dataset.city,
    state: i.dataset.state,
    country: i.dataset.countryDescription,
    phoneNumber: i.dataset.contact,
  })));

  const dataResult = dataPropertyOuter
    .map((v, i) => ({ ...v, ...dataPropertyInner[i] }));

  /* eslint-disable no-restricted-syntax */
  for await (const locationObject of dataResult) {
    const poiData = {
      locator_domain: 'marriott.com__search__findHotels.mi',
      location_name: locationObject.hotelName,
      ...((locationObject.phoneNumber === '' || locationObject.phoneNumber === undefined) && { street_address: locationObject.address }),
      ...((locationObject.phoneNumber !== '' && locationObject.phoneNumber !== undefined) && { street_address: locationObject.address }),
      city: locationObject.city,
      state: locationObject.state,
      zip: removeSpaces(locationObject.postalCode),
      country_code: countryCodeCheck(locationObject.country),
      store_number: undefined,
      phone: formatPhoneNumber(locationObject.phoneNumber),
      location_type: locationObject.brand,
      latitude: locationObject.lat,
      longitude: locationObject.longitude,
      hours_of_operation: undefined,
    };
    const poi = new Poi(poiData);
    await Apify.pushData(poi);
  }
}

module.exports = {
  getLastPage,
  formatPhoneNumber,
  removeSpaces,
  countryCodeCheck,
  pushDetail,
};
