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
  const { city, state, zip } = formatAddressLine2(cityStateZipRaw);
  return {
    street_address,
    city,
    state,
    zip,
    phone,
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
  if (string.includes('ll=')) {
    const a = string.match(/(?=)([-]?[\d]*\.[\d]*),([-]?[\d]*\.[\d]*)(?=&)/g);
    const s = a[0];
    const o = s.split(',');
    return {
      latitude: o[0],
      longitude: o[1],
    };
  }
  if (string.includes('!2d')) {
    const startOfLongitude = string.substring((string.indexOf('!2d') + 3), string.length);
    const startOfLatitude = string.substring((string.indexOf('!3d') + 3), string.length);
    const lat = startOfLatitude.substring(0, startOfLatitude.indexOf('!'));
    const lon = startOfLongitude.substring(0, startOfLongitude.indexOf('!'));
    return {
      latitude: lat,
      longitude: lon,
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
  const splitHours = string.split('\n');
  return splitHours.join(', ');
};

module.exports = {
  parseAddress,
  parseGoogleMapsUrl,
  formatHours,
};
