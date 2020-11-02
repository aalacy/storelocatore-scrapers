const uuidv1 = require('uuid/v1');
const { states } = require('./states');

const noDataLabel = 'NO-DATA';

const cleanStoreInfo = (string) => {
  const clean = string
    .replace(/\t/g, '')
    .replace(/ +(?= )/g, '')
    .replace(/: \\n/, '')
    .replace(/\n/g, ',')
    .replace(/(,,)/g, ',')
    .replace(/\s\s+/g, ' ')
    .replace(/\\/g, '')
    .replace(/,+/g, ',')
    .replace(/:\s,/g, ':')
    .trim();
  if (clean[0] === ',') {
    return clean.substring(1, clean.length).match(/(?=\S)[^,]+?(?=\s*(,|$))/g);
  }
  return clean.match(/(?=\S)[^,]+?(?=\s*(,|$))/g);
};

const stateZip = (string) => {
  if (!string) {
    return undefined;
  }
  if (states.includes(string.substring(0, 2)) && string.length > 5) {
    const state = string.substring(0, string.indexOf(' '));
    const zip = string.substring(string.indexOf(' '), string.length).replace(/\s/g, '');
    return { state, zip };
  }
  if (states.includes(string.substring(0, 2)) && string.length < 5) {
    const state = string.substring(0, 2);
    return { state, zip: undefined };
  }
  return string;
};

const formatPhoneNumber = (string) => {
  if (!string) {
    return undefined;
  }
  const number = string.replace(/\D/g, '');
  if (number.length < 9) {
    return undefined;
  }
  if (number.length > 10) {
    return number.substring(0, 9);
  }
  return number;
};

const addressLine2 = (array) => {
  const arrayCopy = array.slice();
  const possibleStateAbbr = arrayCopy[3].substring(0, 2);
  if (states.indexOf(possibleStateAbbr) > -1) {
    return arrayCopy;
  }
  return arrayCopy.map((v, i, a) => {
    if (i === 1) {
      return `${v}, ${a[i + 1]}`;
    }
    if (i === 2) {
      return false;
    }
    return v;
  }).filter(e => e !== false);
};

const hoursFormat = (array) => {
  const arrayCopy = array.slice();
  if (!arrayCopy[5]) {
    arrayCopy[5] = undefined;
    return arrayCopy;
  }
  if (array[5].includes('Direction')) {
    arrayCopy[5] = undefined;
    return arrayCopy;
  }
  if (array[5].includes('Hours')) {
    const hoursCombined = `${array[5]}, ${array[6]}, ${array[7]}`;
    if (hoursCombined.includes('undefined')) {
      return array.map((v, i) => {
        if (i === 5) {
          return hoursCombined.substring(0, (hoursCombined.indexOf('undefined') - 2));
        }
        return v;
      });
    }
    if (hoursCombined.includes('Directions')) {
      return array.map((v, i) => {
        if (i === 5) {
          return hoursCombined.substring(0, (hoursCombined.indexOf('Directions') - 2));
        }
        return v;
      });
    }
    return array.map((v, i) => {
      if (i === 5) {
        return hoursCombined;
      }
      return v;
    });
  }
  return arrayCopy;
};

const parseGoogleMapsUrl = (string) => {
  if (typeof (string) !== 'string') {
    return undefined;
  }
  const a = string.match(/(?=)([-]?[\d]*\.[\d]*),([-]?[\d]*\.[\d]*)(?=&)/g);
  const s = a[0];
  const o = s.split(',');
  return {
    latitude: o[0],
    longitude: o[1],
  };
};

const getStoreID = urlString => urlString.substring((urlString.indexOf('StoreID=') + 8), urlString.length);

const storeKey = (locationName, address) => {
  if (!locationName || !address) {
    const newKey = uuidv1();
    return newKey;
  }
  const key1 = locationName.replace(/[^A-Z0-9]/ig, '').toLowerCase();
  const key2 = address.replace(/[^A-Z0-9]/ig, '').substring(0, 7).toLowerCase();
  const key = `${key1}${key2}`;
  return key;
};

const createStorageObject = (request, page, storageName, selector, locationType) => ({
  request,
  page,
  dataStorageName: storageName,
  selector,
  locationType,
});

// Make a generic function that helps with pulling poi details from page
async function pullFromPage({
  request, page, dataStorageName, selector, locationType,
}) {
  await page.waitForSelector(selector, { waitFor: 'load', timeout: 0 });
  const storeInfo = await page.$$eval(selector, se => se.map(s => s.innerText));
  const storeInfoCleaned = storeInfo.map(e => cleanStoreInfo(e));
  /* eslint-disable no-restricted-syntax */
  for await (const storeData of storeInfoCleaned) {
    const addressLine2Check = addressLine2(storeData);
    const result = hoursFormat(addressLine2Check);
    const stateZipObject = stateZip(result[3]);
    const key = storeKey(result[0], result[1]);
    const initialPoi = {
      locator_domain: 'johnstonmurphy.com',
      location_name: result[0],
      street_address: result[1],
      city: result[2],
      ...stateZipObject,
      country_code: request.userData.country,
      store_number: undefined,
      phone: formatPhoneNumber(result[4]),
      location_type: locationType,
      naics_code: undefined,
      latitude: undefined,
      longitude: undefined,
      hours_of_operation: result[5],
    };
    await dataStorageName.setValue(key, initialPoi);
  }
}

module.exports = {
  stateZip,
  formatPhoneNumber,
  cleanStoreInfo,
  addressLine2,
  hoursFormat,
  parseGoogleMapsUrl,
  getStoreID,
  storeKey,
  createStorageObject,
  pullFromPage,
};


/*
const data = ['Toronto Dominion Centre',
  '66 Wellington Street',
  'Route55',
  'Toronto',
  'ON M5K 1A1',
  'Phone:(416) 214-6395',
  'Hours:Mon-Fri 7am-7pm',
  'Sat-Sun Closed'];
console.log(addressLine2(data));
*/

/* subset of storeInfoCleaned

[ 'Toronto Dominion Centre',
    '66 Wellington Street',
    'Route55',
    'Toronto',
    'ON M5K 1A1',
    'Phone:(416) 214-6395',
    'Hours:Mon-Fri 7am-7pm',
    'Sat-Sun Closed' ],
*/
