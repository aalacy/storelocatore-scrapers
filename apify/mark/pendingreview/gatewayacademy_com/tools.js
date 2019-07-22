const formatLocationName = (string) => {
  if (!string) {
    return undefined;
  }
  return string.replace(/\n/g, ', ').replace(/\t/g, '').replace(/\s\s+/g);
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
    return number.substring(1, 14);
  }
  return number;
};

const extractZipCode = (string) => {
  if (!string) {
    return {
      zip: undefined,
    };
  }
  const possibleZipCodes = string.match(/[0-9]{5}/g);
  let zip;
  if (possibleZipCodes && possibleZipCodes.length > 0) {
    zip = possibleZipCodes[possibleZipCodes.length - 1];
  }
  return {
    zip,
  };
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
  formatLocationName,
  extractZipCode,
  formatPhoneNumber,
  formatHours,
};
