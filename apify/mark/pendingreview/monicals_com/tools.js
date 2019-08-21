const formatAddress = (string) => {
  if (!string) {
    return undefined;
  }
  const replaceSpacers = string.replace(/\n/g, '').replace(/\t/g, '');
  const trimAddress = replaceSpacers.trim();
  return trimAddress;
};

const formatHours = (string) => {
  if (!string) {
    return undefined;
  }
  const hoursRaw = string.trim();
  const hoursChangeNewLines = hoursRaw.replace(/\n/g, ', ').replace(/\t/g, '').replace('Hours', '');
  return hoursChangeNewLines;
};

module.exports = {
  formatAddress,
  formatHours,
};
