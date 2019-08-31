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

  const removeTabs = string.replace(/\t+/g, '');
  const removeSpan = removeTabs.substring(0, removeTabs.indexOf('<span'));
  const trimmedString = removeSpan.trim();
  const formatSpaces = trimmedString.replace(/\s\s+/g, ',');
  const amountOfCommas = (formatSpaces.match(/,/g) || []).length;

  /* eslint-disable camelcase */
  let streetAddress;
  if (amountOfCommas === 3) {
    streetAddress = formatSpaces.substring(0, (formatSpaces.indexOf(',', formatSpaces.indexOf(',') + 1)));
  }
  if (amountOfCommas === 2) {
    streetAddress = formatSpaces.substring(0, (formatSpaces.indexOf('<br>') + 4));
  }
  const street_address = streetAddress.replace('<br>', '');
  const removedStreet = formatSpaces.substring(streetAddress.length + 1, formatSpaces.length);
  const city = removedStreet.substring(0, removedStreet.indexOf(','));
  const removedCity = removedStreet.substring((city.length + 1), removedStreet.length).trim();
  const startOfZipCode = removedCity.match(/\d/);
  const startOfZipIndex = removedCity.indexOf(startOfZipCode);
  const state = removedCity.substring(0, startOfZipIndex);
  const zip = removedCity.substring(state.length, removedCity.length);
  return {
    street_address,
    city,
    state,
    zip,
  };
};

const parseGoogleMapsUrl = (string) => {
  if (typeof (string) !== 'string') {
    return {
      longitude: undefined,
      latitude: undefined,
    };
  }
  if (string.includes('/@')) {
    const startOfGeo = string.substring((string.indexOf('/@') + 2));
    const splitGeo = startOfGeo.split(',');
    return {
      latitude: splitGeo[0],
      longitude: splitGeo[1],
    };
  }
  if (string.includes('&sll=')) {
    const a = string.match(/(?=)([-]?[\d]*\.[\d]*),([-]?[\d]*\.[\d]*)(?=&)/g);
    const s = a[0];
    const o = s.split(',');
    return {
      latitude: o[0],
      longitude: o[1],
    };
  }
  return {
    longitude: undefined,
    latitude: undefined,
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
  formatAddress,
  parseGoogleMapsUrl,
  formatHours,
  formatData,
};
