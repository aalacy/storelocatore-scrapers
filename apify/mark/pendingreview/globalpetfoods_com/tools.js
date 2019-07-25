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

const extractLocationInfo = (streetAddress, cityStateZip) => {
  if (!streetAddress || !cityStateZip) {
    return {
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
    };
  }
  /* eslint-disable camelcase */
  const genericAddress = `${streetAddress}, ${cityStateZip}`;
  const parsed = parser.parseLocation(genericAddress);
  let street_address;
  let state;
  let city;
  let zip;
  if (parsed) {
    ({ state, city, zip } = parsed);
    street_address = streetAddress;
  }
  if (!parsed || !parsed.state) {
    street_address = streetAddress;
    const addressLine2 = cityStateZip;
    city = addressLine2.substring(0, addressLine2.indexOf(','));
    const removedCity = addressLine2.substring((addressLine2.indexOf(',') + 1), addressLine2.length);
    state = removedCity.substring(1, removedCity.indexOf(','));
    const removedState = removedCity.substring((removedCity.indexOf(',') + 1), removedCity.length);
    zip = removedState.trim();
  }

  return {
    street_address,
    state,
    city,
    zip,
  };
};

const formatHours = (string) => {
  if (!string) {
    return undefined;
  }
  const hoursRaw = string.trim();
  const hoursChangeNewLines = hoursRaw.replace(/\n/g, ', ').replace(/\t/g, '');
  return hoursChangeNewLines;
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
  formatPhoneNumber,
  formatHours,
  storeKey,
};
