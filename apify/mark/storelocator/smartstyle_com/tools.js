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
  if (!string) {
    return undefined;
  }
  const hoursRaw = string.trim();
  const hoursChangeNewLines = hoursRaw.replace(/\n/g, '').replace(/\t/g, '').replace(/\s\s+/g, '');
  return hoursChangeNewLines;
};

module.exports = {
  formatPhoneNumber,
  formatAddress,
  formatHours,
};
