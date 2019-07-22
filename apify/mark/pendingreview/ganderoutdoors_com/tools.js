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

const extractLocationInfo = (string, stringHTML) => {
  if (!string) {
    return {
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
    };
  }
  /* eslint-disable camelcase */
  const cleanString = stringHTML.replace(/\n/g, '').replace(/\s\s+/g, '');
  const streetAddress = cleanString.substring(0, (cleanString.indexOf('<br>')));
  const removeStreetAddress = cleanString.substring((cleanString.indexOf('<br>') + 4), cleanString.length);
  const cityStateZip = removeStreetAddress.substring(0, (removeStreetAddress.indexOf('<br>'))).trim();
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
  formatHours,
};
