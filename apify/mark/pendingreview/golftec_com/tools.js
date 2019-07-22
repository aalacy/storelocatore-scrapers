const formatObject = (string) => {
  const trimmedString = string.trim();
  const jsonObject = JSON.parse(trimmedString);
  return jsonObject;
};

const formatCountry = (string) => {
  if (!string) {
    return undefined;
  }
  const lowerCaseCountry = string.toLowerCase();
  if (lowerCaseCountry === 'united states') {
    return 'US';
  }
  if (lowerCaseCountry === 'canada') {
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


const formatHours = (array) => {
  if (!array) {
    return undefined;
  }
  const hoursRaw = array;
  const combineHours = hoursRaw.map((e) => {
    const day = e.dayOfWeek.replace('http://schema.org/', '');
    return `${day} ${e.opens} - ${e.closes}`;
  });
  return combineHours.join(', ');
};

const storeKey = (address) => {
  if (!address) {
    const newKey = uuidv1();
    return newKey;
  }
  const key = address.replace(/[^A-Z0-9]/ig, '').substring(0, 7).toLowerCase();
  return key;
};

module.exports = {
  formatObject,
  formatCountry,
  formatPhoneNumber,
  formatHours,
  storeKey,
};
