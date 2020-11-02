const parseObject1 = (string) => {
  if (!string) {
    return undefined;
  }
  const splitInfo = string.split('\n');
  const [location_name, street_address, phone] = splitInfo;
  return {
    location_name,
    street_address,
    phone,
  };
};

const formatObject = (string) => {
  const trimmedString = string.trim();
  const jsonObject = JSON.parse(trimmedString);
  return jsonObject;
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

const formatCountry = (string) => {
  if (!string) {
    return undefined;
  }
  const lowerCaseCountry = string.toLowerCase();
  if (lowerCaseCountry === 'usa') {
    return 'US';
  }
  if (lowerCaseCountry === 'united states') {
    return 'US';
  }
  return undefined;
};

const cleanState = (string) => {
  if (!string) {
    return undefined;
  }
  return string.trim().replace(',', '');
};

module.exports = {
  parseObject1,
  formatObject,
  formatAddressLine2,
  formatCountry,
  cleanState,
};
