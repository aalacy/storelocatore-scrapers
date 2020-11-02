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

const formatLocationString = (string) => {
  if (!string) {
    return {
      location_name: undefined,
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
    };
  }
  const removeSpaces = string.replace(/\s\s+/g, '');
  const trimmedString = removeSpaces.trim();
  /* eslint-disable camelcase */
  const location_name = trimmedString.substring(0, trimmedString.indexOf('\n'));
  const removedName = trimmedString.substring(trimmedString.indexOf('\n') + 1, trimmedString.length);
  const street_address = removedName.substring(0, removedName.indexOf('\n'));
  const addressLine2 = removedName.substring(removedName.indexOf('\n'), removedName.length);
  const cityStateZip = formatAddressLine2(addressLine2);

  return {
    location_name,
    street_address,
    ...cityStateZip,
  };
};

module.exports = {
  formatLocationString,
};
