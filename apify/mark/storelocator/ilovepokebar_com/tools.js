const parser = require('parse-address');

const formatPhoneNumber = (string) => {
  if (!string) {
    return undefined;
  }
  const number = string.replace(/\D/g, '');
  if (number.length < 8) {
    return undefined;
  }
  if (number.length > 10) {
    return number.substring(1, 14);
  }
  return number;
};

const extractLocationInfo = (streetAddress, cityStateZip) => {
  if (!streetAddress || !cityStateZip) {
    return {
      street_address: undefined,
      city: undefined,
      state: undefined,
      zip: undefined,
    };
  }
  /* eslint-disable camelcase */
  const genericAddress = `${streetAddress}, ${cityStateZip}`;
  const parsed = parser.parseLocation(genericAddress);
  let street_address;
  let state;
  let city;
  let zip;
  if (parsed && parsed.state) {
    ({ state, city, zip } = parsed);
    street_address = streetAddress;
  }
  if (!parsed.state && !genericAddress.includes('New Zealand')) {
    street_address = streetAddress;
    const addressLine2 = cityStateZip;
    city = addressLine2.substring(0, addressLine2.indexOf(','));

    // Was getting an error in validator stating provinces are not states
    // Also getting an error with this zip code: AssertionError: Invalid zip code: V7J 3J7 && V7J3J7
    /*
    const stateRaw = addressLine2.match(/[A-Z]{2}/);
    const testState = stateRaw[0];
    zip = addressLine2.substring((addressLine2.indexOf(testState) + 2), addressLine2.length).replace(/\s/g, '');
    */
  }
  if (genericAddress.includes('New Zealand')) {
    street_address = streetAddress;
    city = '<INACCESSIBLE>';
    zip = '<INACCESSIBLE>';
  }

  return {
    street_address,
    state,
    city,
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
  if (string.includes('?ll')) {
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


module.exports = {
  extractLocationInfo,
  formatPhoneNumber,
  parseGoogleMapsUrl,
};
