const getDataKey = string => string.replace(/#/g, '!').replace(/\s/g, '');

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

const formatAddress = (string) => {
  if (!string) {
    return {
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
    };
  }
  /* eslint-disable camelcase */
  const street_address = string.substring(0, string.indexOf('\n'));
  const addressLine2Raw = string.substring((street_address.length + 1), string.length);
  const addressLine2 = formatAddressLine2(addressLine2Raw);
  const { city, state, zip } = addressLine2;
  return {
    street_address,
    city,
    state,
    zip,
  };
};

const formatHours = (string) => {
  if (!string) {
    return undefined;
  }
  const hoursRaw = string.trim();
  const ch = '\n';
  const regex = new RegExp(`((?:[^${ch}]*${ch}){${1}}[^${ch}]*)${ch}`, 'g');
  const hoursChangeNewLines = hoursRaw.replace(regex, '$1,').replace(/\s\s+/g, ' ');
  return hoursChangeNewLines;
};

module.exports = {
  getDataKey,
  formatPhoneNumber,
  formatAddress,
  formatHours,
};
