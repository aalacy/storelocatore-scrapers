const parser = require('parse-address');
const decode = require('decode-html');

var text = "15257 N Scottsdale Rd, Suite F1-125, Scottsdale, AZ 85254";

const formatLocationName = (string) => {
  const removedNewLine = string.replace(/\n/g, '');
  return removedNewLine.trim();
};

const createGenericAddress = (stringHTML) => {
  const rawString = decode(stringHTML);
  const genericAddress = rawString.replace(/<br>/g, ', ').replace(/\s\s+/g, ' ');
  return genericAddress;
};

const extractLocationInfo = (genericAddress) => {
  if (!genericAddress) {
    return {
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
    };
  }
  /* eslint-disable camelcase */
  const parsed = parser.parseLocation(genericAddress);
  let street_address;
  let state;
  let city;
  let zip;
  if (parsed) {
    ({ state, city, zip } = parsed);
    street_address = genericAddress.substring(0, (genericAddress.lastIndexOf(city) - 2));
  }
  if (!parsed) {
    const zipRaw = genericAddress.match(/[0-9]{5}$/);
    [zip] = zipRaw;
    const removedZip = genericAddress.substring(0, genericAddress.indexOf(zip));
    const addressArray = removedZip.split(',');
    if (addressArray.length === 4) {
      street_address = `${addressArray[0]}, ${addressArray[1]}`;
      city = addressArray[2].trim();
      state = addressArray[3].trim();
    }
    if (addressArray.length === 3) {
      [street_address] = addressArray;
      city = addressArray[1].trim();
      state = addressArray[2].trim();
    }
  }
  return {
    street_address,
    state,
    city,
    zip,
  };
};

const storeKey = (address) => {
  if (!address) {
    const newKey = 'noKey';
    return newKey;
  }
  const key = address.replace(/[^A-Z0-9]/ig, '').substring(0, 7).toLowerCase();
  return key;
};

module.exports = {
  formatLocationName,
  createGenericAddress,
  extractLocationInfo,
  storeKey,
};
