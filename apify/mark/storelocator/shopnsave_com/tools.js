const { parseString } = require('xml2js');

// Converts XML to JSON
const xml2json = xmlString => new Promise((fullfill, reject) => {
  parseString(xmlString, { explicitArray: false }, (err, result) => {
    if (err) {
      reject(err);
    } else {
      fullfill(result);
    }
  });
});

// Makes the a phone number 10 digits with no punctutations
const formatPhoneNumber = string => string.replace(/\D/g, '');

const validateHours = (string1, string2) => {
  if (string1 === undefined || string1.length === 0) {
    return undefined;
  }
  if (string1 !== undefined || string1.length !== 0) {
    if (string2 === undefined || string2.length === 0) {
      return string1;
    }
  }
  return `${string1}, ${string2}`;
};

module.exports = {
  xml2json,
  formatPhoneNumber,
  validateHours,
};
