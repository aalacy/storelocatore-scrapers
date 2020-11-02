const formatHours = (string) => {
  if (!string) {
    return undefined;
  }
  const hoursRaw = string.trim();
  const removeSpacers = hoursRaw.replace(/\s\s+/g, ' ').replace(/\n/g, ', ').replace(/\t/g, '');
  const clipHours = removeSpacers.substring(0, removeSpacers.indexOf('Sunday') + 29);
  return clipHours;
};

const clipStoreNumber = (string) => {
  if (!string) {
    return undefined;
  }
  return string.replace(/\D/g, '');
};

module.exports = {
  formatHours,
  clipStoreNumber,
};
