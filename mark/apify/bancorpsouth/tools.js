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

const formatStreetAddress = (string1, string2) => {
  if (typeof (string2) === 'string') {
    if (string2.length === 0) {
      return string1;
    }
    return `${string1}, ${string2}`;
  }
  return string1;
};

const parseAddress = (a) => {
  if (typeof (a) !== 'string') {
    return undefined;
  }
  const r = {};
  const c = a.indexOf(',');
  r.city = a.slice(0, c);
  const f = a.substring(c + 2);
  const s = f.lastIndexOf(' ');
  r.state = f.slice(0, s);
  r.zip = f.substring(s + 1);
  return r;
};

const checkLocationType = (url) => {
  if (url.includes('branch')) {
    return 'Branch';
  }
  if (url.includes('office')) {
    return 'Office';
  }
  if (url.includes('atm')) {
    return 'ATM';
  }
  return undefined;
};

const checkHours = (string) => {
  if (string.length === 0) {
    return noDataLabel;
  }
  return string;
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
  hours_of_operation: checkHours(hours_of_operation),
});

module.exports = {
  formatPhoneNumber,
  parseGoogleMapsUrl,
  formatStreetAddress,
  parseAddress,
  checkLocationType,
  formatData,
};
