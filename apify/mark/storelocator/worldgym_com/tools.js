const formatObject = (string) => {
  const trimmedString = string.trim();
  const jsonObject = JSON.parse(trimmedString);
  return jsonObject;
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

const formatAddress = (address1, address2) => {
  if (!address1 || address1 === '') {
    return undefined;
  }
  if (!address2 || address2 === '') {
    return address1;
  }
  return `${address1}, ${address2}`;
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
  formatObject,
  formatPhoneNumber,
  formatAddress,
  formatHours,
};
