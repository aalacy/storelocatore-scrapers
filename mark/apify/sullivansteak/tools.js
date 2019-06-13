const cities = require('cities');

const noDataLabel = 'NO-DATA';

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

// Simply receives data from the scrape, then formats it.
const formatData = ({
  // If any data points are undefined / null, return 'NO-DATA'
  locator_domain: locator_domain = noDataLabel,
  location_name: location_name = noDataLabel,
  street_address: street_address = noDataLabel,
  city: city = noDataLabel,
  state: state = noDataLabel,
  zip: zip = noDataLabel,
  country_code: country_code = noDataLabel,
  store_number: store_number = noDataLabel,
  phone: phone = noDataLabel,
  location_type: location_type = noDataLabel,
  naics = noDataLabel,
  latitude: latitude = noDataLabel,
  longitude: longitude = noDataLabel,
  hours_of_operation: hours_of_operation = noDataLabel,
}) => ({
  // Then set the label similar to the template and make adjustments if not labelled
  locator_domain,
  location_name,
  street_address,
  city,
  state,
  zip,
  country_code,
  store_number,
  phone,
  location_type,
  naics_code: naics,
  latitude,
  longitude,
  hours_of_operation,
});

module.exports = {
  formatObject,
  decodeEntities,
  formatPhoneNumber,
  formatStreetAddress,
  formatHours,
  formatData,
};
