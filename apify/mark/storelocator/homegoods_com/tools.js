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
    return number.substring(1, 10);
  }
  return number;
};

const formatStreetAddress = (string) => {
  if (!string) {
    return undefined;
  }
  return string.trim().replace(/\n/g, '').replace(/\s\s+/g, '');
};

const dirtyParse = (string) => {
  const trimmedString = string.trim();
  const street_address = trimmedString.substring(0, (trimmedString.indexOf('<br>') - 1));
  const removeStreetAddress = trimmedString.substring((trimmedString.indexOf('<br>') + 4), trimmedString.length);
  const city = removeStreetAddress.substring(0, removeStreetAddress.indexOf(',')).trim();
  const removeCity = removeStreetAddress.substring((removeStreetAddress.indexOf(',') + 2), removeStreetAddress.length);
  const zipStartChar = removeCity.match(/\d/)[0];
  const state = removeCity.substring(0, removeCity.indexOf(zipStartChar)).trim();
  const zip = removeCity.substring(removeCity.indexOf(zipStartChar), removeCity.length).trim();
  return {
    street_address,
    city,
    state,
    zip,
  };
};

const formatAddress = (string) => {
  if (!string) {
    return {
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
    };
  }
  const trimmedString = string.trim();
  const removeBr = trimmedString.replace(/\s<br>/g, ',');
  const removeSpaces = removeBr.replace(/\n/g, '').replace(/\t/g, '').replace(/\s\s+/g, ' ');
  const addressObject = parser.parseAddress(removeSpaces);

  // Sometimes parse-address fails, so do our own simple parse
  if (!addressObject) {
    return dirtyParse(string);
  }

  const streetAddressRaw = string.substring(0, string.indexOf('<br>'));
  const street_address = formatStreetAddress(streetAddressRaw);
  const { city } = addressObject;
  const { state } = addressObject;
  const { zip } = addressObject;

  return {
    street_address,
    city,
    state,
    zip,
  };
};

const formatHours = (string) => {
  const hoursRaw = string.substring((string.indexOf('<br>') + 4), string.length);
  const hoursRemovedEndBreak = hoursRaw.replace(/<br>/g, '').trim();
  if (!hoursRemovedEndBreak || hoursRemovedEndBreak.length < 3) {
    return undefined;
  }
  return hoursRemovedEndBreak;
};

const removeEmptyStringProperties = object => Object.keys(object).reduce((acc, key) => {
  acc[key] = object[key] === '' ? undefined
    : object[key]; return acc;
}, {});

module.exports = {
  formatPhoneNumber,
  formatAddress,
  formatHours,
  removeEmptyStringProperties,
};
