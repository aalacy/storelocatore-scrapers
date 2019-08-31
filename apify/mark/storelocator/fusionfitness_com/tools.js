const parser = require('parse-address');

const formatPhoneNumber = (string) => {
  if (!string) {
    return undefined;
  }
  const number = string.replace(/\D/g, '');
  if (number.length < 8) {
    return undefined;
  }
  if (number.length > 10) {
    return number.substring(1, 14);
  }
  return number;
};

const extractLocationInfo = (string) => {
  if (!string) {
    return {
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
    };
  }
  /* eslint-disable camelcase */
  const clipAddress = string.substring((string.indexOf('located at ') + 10), string.length);
  const parsed = parser.parseLocation(clipAddress);
  let street_address;
  let state;
  let city;
  let zip;
  if (parsed) {
    ({ state, city, zip } = parsed);
    street_address = clipAddress.substring(0, (clipAddress.indexOf(city) - 2));
  }

  return {
    street_address,
    state,
    city,
    zip,
  };
};

module.exports = {
  extractLocationInfo,
  formatPhoneNumber,
};
