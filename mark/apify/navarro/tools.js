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
  const addressArray = trimmedString.split(',');
  if (addressArray.length === 4) {
    return {
      street_address: addressArray[0],
      city: addressArray[1].trim(),
      state: addressArray[2].trim(),
      zip: addressArray[3].trim(),
    };
  }
  if (addressArray.length === 5) {
    return {
      street_address: addressArray[0] + addressArray[1],
      city: addressArray[2].trim(),
      state: addressArray[3].trim(),
      zip: addressArray[4].trim(),
    };
  }
  return {
    /* eslint-disable camelcase */
    street_address: undefined,
    city: undefined,
    state: undefined,
    zip: undefined,
  };
};

const formatHours = (string) => {
  if (!string) {
    return undefined;
  }
  const hoursRaw = string.trim();
  const hoursChangeNewLines = hoursRaw.replace(/\n/g, ',');
  return hoursChangeNewLines;
};

const formatGeoLocation = (string) => {
  if (!string) {
    return {
      latitude: undefined,
      longitude: undefined,
    };
  }
  const geoRaw = string.substring((string.indexOf('(') + 2), (string.indexOf('<b>') - 3));
  console.log('geo raw');
  console.log(geoRaw);
  const geoArray = geoRaw.split(',');
  return {
    latitude: geoArray[0],
    longitude: geoArray[1],
  };
};

const formatInfoBlock = (string) => {
  if (!string) {
    return {
      location_name: undefined,
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
      phone: undefined,
      hours_of_operation: undefined,
    };
  }
  const location_name = string.substring(0, string.indexOf('\n'));
  const frontOfAddressIndex = location_name.length + 2;
  const removedLocationName = string.substring(frontOfAddressIndex, string.length);
  const addressRaw = removedLocationName.substring(0, removedLocationName.indexOf('\n'));
  const address = formatAddress(addressRaw);
  const frontOfPhoneIndex = addressRaw.length + 1;
  const removedAddress = removedLocationName
    .substring(frontOfPhoneIndex, removedLocationName.length);
  const phoneRaw = removedAddress.substring(0, removedAddress.indexOf('\n'));
  const phone = formatPhoneNumber(phoneRaw);
  const frontOfHoursIndex = phoneRaw.length + 1;
  const removedPhone = removedAddress.substring(frontOfHoursIndex, removedAddress.length);
  const hoursRaw = removedPhone.substring(0, removedPhone.length);
  const hours_of_operation = formatHours(hoursRaw);
  return {
    location_name,
    ...address,
    phone,
    hours_of_operation,
  };
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
  formatGeoLocation,
  formatInfoBlock,
  formatData,
};
