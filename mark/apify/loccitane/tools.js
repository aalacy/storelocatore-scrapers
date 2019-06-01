const noDataLabel = 'NO-DATA';

// Leaves only digits for the phone number
const formatPhoneNumber = (string) => {
  const number = string.replace(/\D/g, '');
  if (number.length === 0) {
    return undefined;
  }
  if (number.length > 10) {
    return number.substring(0, 9);
  }
  return number;
};

const formatGeoString = (string) => {
  if (string === '') {
    return undefined;
  }
  const geoArray = string.split(',');
  return { latitude: geoArray[0], longitude: geoArray[1] };
};

const removeEmptyStrings = (poi) => {
  const objectShallowCopy = Object.assign({}, poi);
  Object.entries(objectShallowCopy).forEach(([key, val]) => {
    if (val === '') {
      objectShallowCopy[key] = undefined;
    }
  });
  return objectShallowCopy;
};

// Simply receives data from the scrape, then formats it.
const formatData = ({
  // If any data points are undefined / null, return 'NO-DATA'
  locator_domain,
  location_name: location_name = noDataLabel,
  street_address: street_address = noDataLabel,
  city: city = noDataLabel,
  state: state = noDataLabel,
  zip: zip = noDataLabel,
  country_code: country_code = noDataLabel,
  store_number: store_number = noDataLabel,
  phone: phone = noDataLabel,
  location_type: location_type = noDataLabel,
  naics: naics = noDataLabel,
  latitude: latitude = noDataLabel,
  longitude: longitude = noDataLabel,
  hours_of_operation: hours_of_operation = noDataLabel,
}) => ({
  // Then set the label similar to the template and make adjustments
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
  formatPhoneNumber,
  formatGeoString,
  removeEmptyStrings,
  formatData,
};
