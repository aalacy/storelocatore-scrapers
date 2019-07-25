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

const formatCountry = (string) => {
  if (!string) {
    return undefined;
  }
  const lowerCaseCountry = string.toLowerCase();
  if (lowerCaseCountry === 'united states') {
    return 'US';
  }
  if (lowerCaseCountry === 'canada') {
    return 'CA';
  }
  return undefined;
};

const extractLocationInfo = (string) => {
  if (!string) {
    return {
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
      phone: undefined,
      hours_of_operation: undefined,
    };
  }
  /* eslint-disable camelcase */
  const insertSeperators = string.replace(/\n/g, ',');
  const street_address = insertSeperators.substring(0, insertSeperators.indexOf(','));
  const removedAddress = insertSeperators
    .substring((street_address.length + 2), insertSeperators.length);
  const cityState = removedAddress.substring(0, removedAddress.indexOf(','));
  const stateRaw = cityState.match(/[A-Z]{2}$/);
  const state = stateRaw[0];
  const stateIndex = removedAddress.indexOf(state);
  const city = cityState.substring(0, (stateIndex - 1));
  const removedLine1 = removedAddress.substring((cityState.length + 1), removedAddress.length);
  const phoneRaw = removedLine1.substring(0, removedLine1.indexOf(','));
  const phone = formatPhoneNumber(phoneRaw);
  const removedPhone = removedLine1.substring((phoneRaw.length + 1), removedLine1.length);
  const hours_of_operation = removedPhone;

  return {
    street_address,
    state,
    city,
    phone,
    hours_of_operation,
  };
};

module.exports = {
  extractLocationInfo,
  formatCountry,
};
