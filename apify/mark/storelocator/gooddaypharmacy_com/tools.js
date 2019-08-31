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
  return {
    street_address,
    state,
    city,
    zip,
  };
};

const parseGoogleMapsUrl = (string) => {
  if (!string || !string.includes('!2d')) {
    return {
      latitude: undefined,
      longitude: undefined,
    };
  }
  const longitude = string.substring(string.indexOf('!2d') + 3, string.indexOf('!2d') + 12);
  const latitude = string.substring(string.indexOf('!3d') + 3, string.indexOf('!3d') + 12);
  return {
    latitude,
    longitude,
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

module.exports = {
  extractLocationInfo,
  formatPhoneNumber,
  parseGoogleMapsUrl,
  formatHours,
};
