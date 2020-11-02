const formatHours = (string) => {
  if (!string) {
    return undefined;
  }
  const hoursRaw = string.trim();
  const hoursChangeNewLines = hoursRaw.replace(/\n/g, ', ').replace(/\t/g, '');
  return hoursChangeNewLines;
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

const removeEmptyStringProperties = object => Object.keys(object).reduce((acc, key) => {
  acc[key] = object[key] === '' ? undefined
    : object[key]; return acc;
}, {});

module.exports = {
  formatHours,
  formatPhoneNumber,
  removeEmptyStringProperties,
};
