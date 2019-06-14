const Apify = require('apify');
const _ = require('lodash');

const noDataLabel = 'NO-DATA';

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

// Simply receives data from the scrape, then formats it.
const formatData = ({
  // If any data points are undefined / null, return 'NO-DATA'
  locator_domain: locator_domain = noDataLabel,
  location_name: location_name = noDataLabel,
  street_address: street_address = noDataLabel,
  city: city = noDataLabel,
  state: state = noDataLabel,
  zip: zip = noDataLabel,
  country_code: country_code = noDataLabel,
  store_number: store_number = noDataLabel,
  phone: phone = noDataLabel,
  location_type: location_type = noDataLabel,
  naics = noDataLabel,
  latitude: latitude = noDataLabel,
  longitude: longitude = noDataLabel,
  hours_of_operation: hours_of_operation = noDataLabel,
}) => ({
  // Then set the label similar to the template and make adjustments if not labelled
  locator_domain,
  location_name,
  street_address,
  city,
  state,
  zip,
  country_code,
  store_number,
  phone,
  location_type,
  naics_code: naics,
  latitude,
  longitude,
  hours_of_operation,
});

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
    const poi = {
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
      naics_code: undefined,
      latitude: locationObject.lat,
      longitude: locationObject.longitude,
      hours_of_operation: undefined,
    };

    await Apify.pushData(formatData(poi));
  }
}

module.exports = {
  getLastPage,
  formatPhoneNumber,
  removeSpaces,
  countryCodeCheck,
  formatData,
  pushDetail,
};
