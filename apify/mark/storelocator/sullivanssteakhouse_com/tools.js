const cities = require('cities');

const formatObject = (string) => {
  const trimmedString = string.trim();
  const jsonObject = JSON.parse(trimmedString);
  return jsonObject;
};

const decodeEntities = (encodedString) => {
  const translateReg = /&(nbsp|amp|quot|lt|gt);/g;
  const translate = {
    nbsp: ' ',
    amp: '&',
    quot: '"',
    lt: '<',
    gt: '>',
  };
  return encodedString.replace(translateReg, (match, entity) => translate[entity])
    .replace(/&#(\d+);/gi, (match, numStr) => {
      const num = parseInt(numStr, 10);
      return String.fromCharCode(num);
    });
};

const cleanString = (string) => {
  if (!string) {
    return undefined;
  }
  return string.replace(/\t/g, '').replace(/\n/g, '');
};

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

const formatStreetAddress = (unformattedString, zipCode) => {
  if (!unformattedString) {
    return undefined;
  }
  const cityObject = cities.zip_lookup(zipCode);
  const streetRaw = unformattedString
    .substring(0, (unformattedString.indexOf(cityObject.city) - 1));
  const result = streetRaw.trim();
  if (result[result.length - 1] === ',') {
    return result.substring(0, ((result.length - 1)));
  }
  return cleanString(result);
};

const formatHours = (string) => {
  if (!string) {
    return undefined;
  }
  return string.replace(/\n/g, ', ');
};

module.exports = {
  formatObject,
  decodeEntities,
  formatPhoneNumber,
  formatStreetAddress,
  formatHours,
};
