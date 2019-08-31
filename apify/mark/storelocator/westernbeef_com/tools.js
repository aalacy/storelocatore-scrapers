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
  const addressObject = parser.parseLocation(string);
  const {
    suffix,
    type,
    city,
    state,
    zip,
  } = addressObject;
  /* eslint-disable camelcase */
  let resultCity = city;
  let street_address;
  const invalidTypes = ['Mt', 'Lk'];
  const invalidSuffix = ['E', 'W'];
  const transformSuffix = (suff) => {
    switch (suff) {
      case 'E':
        return 'East';
      case 'W':
        return 'W.';
      default:
        break;
    }
    return string;
  };
  if (invalidTypes.some(e => e === type)) {
    resultCity = `${type} ${city}`;
    street_address = string.substring(0, (string.indexOf(resultCity[0]) - 1));
  } else if (invalidSuffix.some(e => e === suffix)) {
    const newSuffix = transformSuffix(suffix);
    resultCity = `${newSuffix} ${city}`;
    street_address = string.substring(0, (string.indexOf(resultCity) - 1));
  } else {
    street_address = string.substring(0, (string.indexOf(resultCity) - 1));
  }
  return {
    street_address,
    city: resultCity,
    state,
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

const formatHours = (string) => {
  if (!string) {
    return undefined;
  }
  const hoursRaw = string.trim();
  const hoursChangeNewLines = hoursRaw.replace(/\n/g, ', ').replace(/\t/g, '');
  return hoursChangeNewLines;
};

module.exports = {
  formatAddress,
  formatPhoneNumber,
  parseGoogleMapsUrl,
  formatHours,
};
