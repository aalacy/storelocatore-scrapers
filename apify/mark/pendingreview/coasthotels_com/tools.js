const cleanState = (string) => {
  if (!string) {
    return undefined;
  }
  return string.trim().replace(',', '');
};

const formatAddressLine2 = (string) => {
  if (!string) {
    return {
      city: undefined,
      state: undefined,
      zip: undefined,
    };
  }
  /* eslint-disable camelcase */
  const splitLine2 = string.split(',');
  const cityState = splitLine2[0];
  const zip = splitLine2[1].trim();
  const [state] = cityState.match(/[A-Z]{2}/);
  const city = cityState.substring(0, cityState.indexOf(state)).trim();
  return {
    city,
    state,
    zip,
  };
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

const parseAddress = (string) => {
  if (!string) {
    return {
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
      phone: undefined,
    };
  }
  let phone;
  const splitAddress = string.split('\n');
  const street_address = splitAddress[0];
  const cityStateZipRaw = splitAddress[1];
  if (splitAddress.length === 2) {
    phone = undefined;
  } else {
    [, , phone] = splitAddress;
  }
  phone = formatPhoneNumber(phone);
  const { city, state, zip } = formatAddressLine2(cityStateZipRaw);
  return {
    street_address,
    city,
    state,
    zip,
    phone,
  };
};

module.exports = {
  cleanState,
  parseAddress,
};
