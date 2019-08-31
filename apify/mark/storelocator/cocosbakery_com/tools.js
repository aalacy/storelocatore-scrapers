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
  const removeSpaces = string.replace(/\s\s+/g, '');
  const trimmedString = removeSpaces.trim();
  /* eslint-disable camelcase */
  const street_address = trimmedString.substring(0, (trimmedString.indexOf('<br>')));
  const address2 = trimmedString.substring((trimmedString.indexOf('<br>') + 4), trimmedString.length);
  const stateAbbr = address2.match(/[A-Z][A-Z]/);
  const stateAbbrIndex = address2.indexOf(stateAbbr);
  const city = address2.substring(0, stateAbbrIndex).trim();
  const state = stateAbbr[0];
  const frontOfStateIndex = stateAbbrIndex + state.length + 1;
  const zip = address2.substring(frontOfStateIndex, address2.length).trim();
  return {
    street_address,
    city,
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
  if (string.includes('&sll=')) {
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
  formatPhoneNumber,
  formatAddress,
  formatHours,
  parseGoogleMapsUrl,
};
