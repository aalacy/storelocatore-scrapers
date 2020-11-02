const removeSpaces = (string) => {
  if (!string) {
    return undefined;
  }
  const replaceSpacers = string.replace(/\n/g, '').replace(/\t/g, '');
  const trimAddress = replaceSpacers.trim();
  return trimAddress;
};

const formatGeo = (string) => {
  if (!string) {
    return undefined;
  }
  const clipUrl = string.substring(string.indexOf('destination'), string.length);
  const clipToLatitude = clipUrl.substring((clipUrl.indexOf('=') + 1), clipUrl.length);
  const splitGeo = clipToLatitude.split(',');
  return {
    latitude: splitGeo[0],
    longitude: splitGeo[1],
  };
};

module.exports = {
  removeSpaces,
  formatGeo,
};
