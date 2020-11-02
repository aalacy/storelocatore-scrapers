const formatLocationName = (string) => {
  if (!string) {
    return undefined;
  }
  return string.replace(/\n/g, ', ').replace(/\t/g, '').replace(/\s\s+/g);
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
    return number.substring(1, 14);
  }
  return number;
};

const extractZipCode = (string) => {
  if (!string) {
    return {
      zip: undefined,
    };
  }
  const possibleZipCodes = string.match(/[0-9]{5}/g);
  let zip;
  if (possibleZipCodes && possibleZipCodes.length > 0) {
    zip = possibleZipCodes[possibleZipCodes.length - 1];
  }
  return {
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
  if (string.includes('ll=')) {
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
  formatLocationName,
  extractZipCode,
  formatPhoneNumber,
  parseGoogleMapsUrl,
  formatHours,
};
