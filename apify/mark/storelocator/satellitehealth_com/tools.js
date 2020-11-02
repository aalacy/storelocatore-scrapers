const upperCaseWords = string => string.toLowerCase()
  .split(' ')
  .map(s => s.charAt(0).toUpperCase() + s.substring(1))
  .join(' ');

const formatHours = (string) => {
  if (!string) {
    return undefined;
  }
  const hoursRaw = string.trim();
  const hoursChangeNewLines = hoursRaw.replace(/\n/g, ', ').replace(/\t/g, '');
  return hoursChangeNewLines;
};

const storeKey = (latitude) => {
  if (!latitude) {
    const newKey = 'noKey';
    return newKey;
  }
  const key = latitude.replace(/[^A-Z0-9]/ig, '').substring(0, 7).toLowerCase();
  return key;
};

module.exports = {
  upperCaseWords,
  formatHours,
  storeKey,
};
