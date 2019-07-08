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

module.exports = {
  formatObject,
  formatPhoneNumber,
};
