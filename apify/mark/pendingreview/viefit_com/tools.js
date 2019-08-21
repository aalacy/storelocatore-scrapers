const formatObject = (string) => {
  const trimmedString = string.trim();
  const jsonObject = JSON.parse(trimmedString);
  return jsonObject;
};

module.exports = {
  formatObject,
};
