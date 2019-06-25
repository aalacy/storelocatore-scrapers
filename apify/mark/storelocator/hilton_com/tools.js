const noDataLabel = 'NO-DATA';

const formatObject = (string) => {
  const trimmedString = string.trim();
  const jsonObject = JSON.parse(trimmedString);
  return jsonObject;
};

const formatLocationObject = (string) => {
  const trimmedString = string.trim();
  const copyFrontDescription = trimmedString.substring(0, (trimmedString.indexOf('description') - 2));
  const clipFrontDescription = trimmedString.substring(trimmedString.indexOf('description'), trimmedString.length);
  const copyAfterDescription = clipFrontDescription.substring((clipFrontDescription.indexOf('openingHours') - 1), clipFrontDescription.length);
  const removedDescription = copyFrontDescription + copyAfterDescription;
  const fixedQuotation = removedDescription.replace(/'/g, '"').replace(/'/g, '"');
  const replaceEndingComma = fixedQuotation.replace(/,([^,]*)$/, '$1');
  const jsonObject = JSON.parse(replaceEndingComma);
  return jsonObject;
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
  formatLocationObject,
  formatObject,
  formatPhoneNumber,
  formatData,
};
