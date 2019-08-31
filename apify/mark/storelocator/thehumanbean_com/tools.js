const { statesLowerCase } = require('./states');

// Leaves only digits for the phone number
const formatPhoneNumber = (string) => {
  const number = string.replace(/\D/g, '');
  if (number.length === 0) {
    return undefined;
  }
  if (number.length > 10) {
    return number.substring(0, 9);
  }
  return number;
};

const formatHours = (string) => {
  if (string) {
    return string.replace(/(?:\r\n|\r|\n)/g, ', ');
  }
  return undefined;
};

const parseAddress = (string) => {
  if (string) {
    // const removeSpaces = string.replace(/\s/g, '');
    const addressOnly = string.substring((string.indexOf('BEAN') + 4), string.length);
    const addressArray = addressOnly.split(',');
    const streetAddress = addressArray[0].trim();
    const addressLocality = addressArray[1].trim();
    const endAddress = addressArray[2];
    const zip = endAddress.substring(addressArray[2].search(/[0-9]/), addressArray[2].length);
    const addressEnd = addressArray[2].split(/[0-9]/);
    const stateName = addressEnd[0].trim();
    const addressRegion = statesLowerCase[stateName.toLowerCase()];
    return {
      streetAddress,
      addressLocality,
      addressRegion,
      zip,
    };
  }
  return undefined;
};

module.exports = {
  formatPhoneNumber,
  formatHours,
  parseAddress,
};
