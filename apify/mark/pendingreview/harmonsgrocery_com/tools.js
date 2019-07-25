const parser = require('parse-address');
const decode = require('decode-html');

const formatObject = (string) => {
  const trimmedString = string.trim();
  const jsonObject = JSON.parse(trimmedString);
  return jsonObject;
};

const createGenericAddress = (stringHTML) => {
  const rawString = decode(stringHTML);
  let genericAddress;
  if (rawString.includes('Harmons')) {
    genericAddress = rawString.substring((rawString.indexOf('<br>') + 4), rawString.length).trim();
  } else {
    genericAddress = rawString.replace(/<br>/g, ',');
  }
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
    const removeLastPeriod = genericAddress.replace(/.([^.]*)$/, '$1');
    street_address = removeLastPeriod.substring(0, (removeLastPeriod.lastIndexOf(city) - 2));
  }
  return {
    street_address,
    state,
    city,
    zip,
  };
};

module.exports = {
  formatObject,
  createGenericAddress,
  extractLocationInfo,
};
