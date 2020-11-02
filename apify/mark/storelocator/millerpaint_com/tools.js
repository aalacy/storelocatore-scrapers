const parser = require('parse-address');

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
    street_address = genericAddress.substring(0, (genericAddress.indexOf(city) - 2));
    if (!state) {
      state = '<INACCESSIBLE>';
    }
    if (!city) {
      city = '<INACCESSIBLE>';
    }
    if (!zip) {
      zip = '<INACCESSIBLE>';
    }
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
  extractLocationInfo,
  storeKey,
};
