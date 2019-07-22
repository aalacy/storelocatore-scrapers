const parser = require('parse-address');
const decode = require('decode-html');

const createGenericAddress = (stringHTML) => {
  const rawString = decode(stringHTML);
  let genericAddress;
  if (rawString.includes('Harmons')) {
    genericAddress = rawString.substring((rawString.indexOf('<br>') + 4), rawString.length).trim();
  } else {
    genericAddress = rawString.replace('<br>', ',');
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
    street_address = genericAddress.substring(0, (genericAddress.indexOf(city) - 2));
  }
  return {
    street_address,
    state,
    city,
    zip,
  };
};

module.exports = {
  createGenericAddress,
  extractLocationInfo,
};
