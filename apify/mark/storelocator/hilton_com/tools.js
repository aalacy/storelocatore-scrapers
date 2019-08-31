const formatCountry = (string) => {
  if (string === 'USA') {
    return 'US';
  }
  if (string === 'Canada') {
    return 'CA';
  }
  return undefined;
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

const formatGeo = (string) => {
  const splitGeoArray = string.split(';');
  return {
    latitude: splitGeoArray[0],
    longitude: splitGeoArray[1],
  };
};

module.exports = {
  formatPhoneNumber,
  formatCountry,
  formatGeo,
};
