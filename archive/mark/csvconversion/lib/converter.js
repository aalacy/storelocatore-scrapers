const { parseString } = require('xml2js');

// Warning does not work for arrays with deeply nested objects. Arrays should be of equal length
const combineObjArray = (array1, array2) => {
  const firstArray = array1.slice();
  const secondArray = array2.slice();
  return firstArray.map((currentVal, index, arr) => {
    return { ...currentVal, ...secondArray[index] };
  });
};

const formatPhoneNumber = string => {
  return string.replace(/\D/g, '');
};

const removeSpaces = string => {
  return string.replace(/\s/g, '');
};

const countryCode = string => {
  if (string === 'Canada') {
    return 'CA';
  }
  if (string === 'USA') {
    return 'US';
  }
  return 'NO-DATA';
};

const sanitizeInput = string => {
  return string
    .replace(',', '')
    .replace('"', '')
    .replace('"', '');
};

const validateData = anything => {
  if (anything === undefined || anything === null) {
    return 'NO-DATA';
  }
  if (anything.length < 1) {
    return 'NO-DATA';
  }
  return anything;
};

// Simply remove white spaces zip code and formats the phone number to 10 digits for Marriot Hotels. Also changes country to code.
const formatInnerArray = array => {
  const arrayCopy = array.slice();
  for (const x of array) {
    x.address = validateData(x.address);
    x.postalCode = validateData(x.postalCode);
    x.city = validateData(x.city);
    x.state = validateData(x.state);
    x.country = validateData(x.country);
    x.phoneNumber = validateData(x.phoneNumber);

    if (x.postalCode !== 'NO-DATA') {
      x.postalCode = removeSpaces(x.postalCode);
    }
    if (x.phoneNumber !== 'NO-DATA') {
      x.phoneNumber = formatPhoneNumber(x.phoneNumber);
    }
    if (x.country !== 'NO-DATA') {
      x.country = countryCode(x.country);
    }

    if (x.phoneNumber === 'NO-DATA') {
      x.address = 'coming soon';
    }
  }
  return arrayCopy;
};

const formatOuterArray = array => {
  const arrayCopy = array.slice();
  for (const x of array) {
    x.lat = validateData(x.lat);
    x.longitude = validateData(x.longitude);
    x.brand = validateData(x.brand);
    x.hotelName = validateData(x.hotelName);
  }
  return arrayCopy;
};

const xml2json = xmlString => {
  return new Promise((fullfill, reject) => {
    parseString(xmlString, { explicitArray: false }, (err, result) => {
      if (err) {
        reject(err);
      } else {
        fullfill(result);
      }
    });
  });
};

module.exports = {
  combineObjArray,
  formatPhoneNumber,
  removeSpaces,
  formatInnerArray,
  xml2json,
  sanitizeInput,
};
