const noDataLabel = 'NO-DATA';

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

const formatGeoLocation = (string) => {
  const locations = string.replace(/\s/g, '').split(',');
  return { latitude: locations[0], longitude: locations[1] };
};
const formatCityState = (string) => {
  const noSpaces = string.replace(/\s/g, '');
  const formatted = noSpaces.split(',');
  return { city: formatted[0], state: formatted[1] };
};

const formatStreetAddress = (address) => {
  if (address.includes('(')) {
    return address.substring(0, (address.indexOf('(') - 1));
  }
  return address;
};

const formatHours = (string1, string2) => {
  if (string1.length === 0) {
    return noDataLabel;
  }
  if (string1.length > 0) {
    if (string2 === 0) {
      return string1;
    }
    if (string1.length > 0 && string2.length > 0) {
      return `${string1}, ${string2}`;
    }
  }
  return undefined;
};

module.exports = {
  formatGeoLocation,
  formatCityState,
  formatStreetAddress,
  formatPhoneNumber,
  formatHours,
};
