const formatObject = (string) => {
  const trimmedString = string.trim();
  const jsonObject = JSON.parse(trimmedString);
  return jsonObject;
};

const formatLocationObject = (string) => {
  const trimmedString = string.trim();
  const copyFrontDescription = trimmedString.substring(0, (trimmedString.indexOf('description') - 2));
  const clipFrontDescription = trimmedString.substring(trimmedString.indexOf('description'), trimmedString.length);
  const copyAfterDescription = clipFrontDescription.substring((clipFrontDescription.indexOf('openingHours') - 1), clipFrontDescription.length);
  const removedDescription = copyFrontDescription + copyAfterDescription;
  const fixedQuotation = removedDescription.replace(/'/g, '"').replace(/'/g, '"');
  const replaceEndingComma = fixedQuotation.replace(/,([^,]*)$/, '$1');
  const jsonObject = JSON.parse(replaceEndingComma);
  return jsonObject;
};

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

module.exports = {
  formatLocationObject,
  formatObject,
  formatPhoneNumber,
  formatCountry,
};
