const parser = require('parse-address');
const decode = require('decode-html');

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
  const cleanGenericAddress = decode(genericAddress);
  const parsed = parser.parseLocation(cleanGenericAddress);
  let street_address;
  let state;
  let city;
  let zip;
  if (parsed) {
    ({ state, city, zip } = parsed);
    street_address = streetAddress;
  }
  if (!parsed || !parsed.state) {
    street_address = streetAddress;
    const addressLine2 = cityStateZip;
    city = addressLine2.substring(0, addressLine2.indexOf(','));
    const removedCity = addressLine2.substring((addressLine2.indexOf(',') + 1), addressLine2.length);
    state = removedCity.substring(1, removedCity.indexOf(','));
    const removedState = removedCity.substring((removedCity.indexOf(',') + 1), removedCity.length);
    zip = removedState.trim();
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
  if (string.includes('?ll=')) {
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
