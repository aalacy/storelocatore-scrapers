const Entities = require('html-entities').XmlEntities;

const entities = new Entities();

const formatObject = (string) => {
  const trimmedString = string.trim();
  const jsonObject = JSON.parse(trimmedString);
  return jsonObject;
};

const formatName = (string) => {
  if (!string) {
    return undefined;
  }
  return entities.decode(string);
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

const extractLocationType = (string) => {
  if (!string) {
    return undefined;
  }
  const removedBaseUrl = string.replace('https://nortonhealthcare.com/location/', '');
  const locationTypeRaw = removedBaseUrl.substring(0, removedBaseUrl.indexOf('/'));
  const locationType = locationTypeRaw.replace(/-/g, ' ');
  return locationType;
};

const formatHours = (array) => {
  if (!array || array.length < 1) {
    return undefined;
  }
  const hours = array.join(', ');
  if (hours.includes('Please Call For Hours')) {
    return undefined;
  }
  const cleanedHours = hours.replace(/\n/g, '').replace(/\s\s+/g, '');
  return cleanedHours;
};

module.exports = {
  formatObject,
  formatName,
  formatPhoneNumber,
  extractLocationType,
  formatHours,
};
