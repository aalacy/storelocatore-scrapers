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

const formatGeoLocation = (string) => {
  const locations = string.replace(/\s/g, '').split(',');
  return { latitude: locations[0], longitude: locations[1] };
};
const formatCityState = (string) => {
  const noSpaces = string.replace(/\s/g, '');
  const formatted = noSpaces.split(',');
  return { city: formatted[0], state: formatted[1] };
};

const formatStreetAddress = (address) => {
  if (address.includes('(')) {
    return address.substring(0, (address.indexOf('(') - 1));
  }
  return address;
};

const formatHours = (string1, string2) => {
  if (string1.length === 0) {
    return noDataLabel;
  }
  if (string1.length > 0) {
    if (string2 === 0) {
      return string1;
    }
    if (string1.length > 0 && string2.length > 0) {
      return `${string1}, ${string2}`;
    }
  }
  return undefined;
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
  formatGeoLocation,
  formatCityState,
  formatStreetAddress,
  formatPhoneNumber,
  formatHours,
  formatData,
};
