const Entities = require('html-entities').XmlEntities;

const entities = new Entities();

const formatName = (string) => {
  if (!string) {
    return undefined;
  }
  const fixNewLine = string.replace('\n', ' ');
  return entities.decode(fixNewLine);
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

const formatHours = (string) => {
  if (!string) {
    return undefined;
  }
  const hoursRaw = string.trim();
  const hoursChangeNewLines = hoursRaw.replace(/\n/g, ', ').replace(/\t/g, '');
  return hoursChangeNewLines;
};

module.exports = {
  formatName,
  formatPhoneNumber,
  formatHours,
};
