const noDataLabel = 'NO-DATA';

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

const formatAddressLine1 = (string) => {
  if (!string) {
    return undefined;
  }
  const firstDigit = string.match(/\d/);
  const indexFirstDigit = string.indexOf(firstDigit);
  return string.substring(indexFirstDigit, string.length);
};

const formatAddressLine2 = (string) => {
  if (!string) {
    return {
      city: undefined,
      state: undefined,
      zip: undefined,
    };
  }
  const trimmedString = string.trim();
  /* eslint-disable camelcase */
  const city = trimmedString.substring(0, trimmedString.indexOf(','));
  const frontOfCityIndex = city.length + 2;
  const state = trimmedString.substring(frontOfCityIndex, frontOfCityIndex + 3).trim();
  const frontOfStateIndex = trimmedString.indexOf(state) + state.length + 1;
  const zip = trimmedString.substring(frontOfStateIndex, trimmedString.length).trim();
  return {
    city,
    state,
    zip,
  };
};

const formatHours = (string) => {
  if (!string) {
    return undefined;
  }
  return string.replace(/\n\n/g, ',');
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
  formatPhoneNumber,
  formatAddressLine1,
  formatAddressLine2,
  formatHours,
  formatData,
};
