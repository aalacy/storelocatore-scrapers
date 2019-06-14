const noDataLabel = 'NO-DATA';

const formatStreetAddress = (string) => {
  if (!string) {
    return undefined;
  }
  const stringArray = string.split(',');
  if (stringArray.length === 4) {
    const removeEnd = stringArray.splice(0, 2);
    const combineToString = removeEnd.join(', ');
    return cleanString(combineToString);
  }
  if (stringArray.length === 3) {
    return cleanString(stringArray[0]);
  }
  return cleanString(string);
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

const formatObject = (string) => {
  const trimmedString = string.trim();
  const jsonObject = JSON.parse(trimmedString);
  return jsonObject;
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
  /* eslint-disable camelcase */
  const street_address = trimmedString.substring(0, (trimmedString.indexOf('<br>') - 1));
  const city = trimmedString.substring((trimmedString.indexOf('<br>') + 4), trimmedString.indexOf(',')).trim();
  const frontOfCityIndex = trimmedString.indexOf(city) + city.length + 2;
  const state = trimmedString.substring(frontOfCityIndex, (frontOfCityIndex + 3)).trim();
  const frontOfStateIndex = trimmedString.indexOf(state) + state.length + 1;
  const zip = trimmedString.substring(frontOfStateIndex, trimmedString.length).trim();
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


const parseGoogleMapsUrl = (string) => {
  if (typeof (string) !== 'string') {
    return undefined;
  }
  const a = string.match(/(?=)([-]?[\d]*\.[\d]*),([-]?[\d]*\.[\d]*)(?=&)/g);
  const s = a[0];
  const o = s.split(',');
  return {
    latitude: o[0],
    longitude: o[1],
  };
};


const noDataLabel = 'NO-DATA';


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

const formatHoursTwoStrings = (string1, string2) => {
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


const formatAddressOneBigChunk = (string) => {
  if (!string) {
    return {
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
    };
  }
  const trimmedString = string.trim();
  /* eslint-disable camelcase */
  const street_address = trimmedString.substring(0, (trimmedString.indexOf('<br>') - 1));
  const city = trimmedString.substring((trimmedString.indexOf('<br>') + 4), trimmedString.indexOf(',')).trim();
  const frontOfCityIndex = trimmedString.indexOf(city) + city.length + 2;
  const state = trimmedString.substring(frontOfCityIndex, (frontOfCityIndex + 3)).trim();
  const frontOfStateIndex = trimmedString.indexOf(state) + state.length + 1;
  const zip = trimmedString.substring(frontOfStateIndex, trimmedString.length).trim();
  return {
    street_address,
    city,
    state,
    zip,
  };
};
