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
      phone: undefined,
    };
  }
  /* eslint-disable camelcase */
  const removeMultiSpace = string.replace(/\s\s+/g, ' ');
  const beginPhoneIndex = removeMultiSpace.indexOf('(');
  let addressLine1 = removeMultiSpace.substring(0, (beginPhoneIndex - 1));
  const addressCity = removeMultiSpace.substring(0, removeMultiSpace.indexOf(','));
  const parsed = parser.parseLocation(addressLine1);
  let street_address;
  let city;
  let state;
  let zip;
  if (!parsed) {
    const areaCode = removeMultiSpace.match(/[0-9]{3}-/);
    addressLine1 = removeMultiSpace.substring(0, removeMultiSpace.indexOf(areaCode[0]));
    const addressCityCopy = addressCity;
    const splitAddressCity = addressCityCopy.split(' ');
    city = splitAddressCity.pop();
    street_address = splitAddressCity.join(' ');
    const removedAddressCity = addressLine1.substring((addressCity.length + 2), addressLine1.length);
    const lowerCaseStateZip = removedAddressCity.toLowerCase();
    const stateRaw = lowerCaseStateZip.match(/[a-z]{2}/);
    const [lowerCaseState] = stateRaw;
    state = lowerCaseState.toUpperCase();
    const zipRaw = lowerCaseStateZip.match(/[0-9]{5}/);
    [zip] = zipRaw;
  } else {
    ({ city, state, zip } = parsed);
    street_address = addressLine1.substring(0, (addressLine1.indexOf(city) - 1)).trim();
  }

  const phoneRaw = removeMultiSpace.substring((addressLine1.length - 1), removeMultiSpace.length);
  const phone = formatPhoneNumber(phoneRaw);

  return {
    street_address,
    state,
    city,
    zip,
    phone,
  };
};

const parseGoogleUrl = (string) => {
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
  const hoursChangeNewLines = hoursRaw.replace(/\n/g, '').replace(/\t/g, '');
  return hoursChangeNewLines;
};

module.exports = {
  extractLocationInfo,
  parseGoogleUrl,
  formatHours,
};
