const parseGeoUrl = (string) => {
  if (!string || !string.includes('cp=')) {
    return {
      latitude: undefined,
      longitude: undefined,
    };
  }
  /* https://www.bing.com/maps?cp=33.30114746093748~-111.90074920654297&lvl=10&style=r&FORM=BMLOGO */
  const clipStart = string.substring((string.indexOf('cp=') + 3), string.length);
  const clipEnd = clipStart.substring(0, clipStart.indexOf('&'));
  const geoArray = clipEnd.split('~');
  return {
    latitude: geoArray[0],
    longitude: geoArray[1],
  };
};

const removeEmptyStringProperties = object => Object.keys(object).reduce((acc, key) => {
  acc[key] = object[key] === '' ? undefined
    : object[key]; return acc;
}, {});

module.exports = {
  parseGeoUrl,
  removeEmptyStringProperties,
};
