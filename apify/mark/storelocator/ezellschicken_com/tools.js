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

const getCityStateZip = (string) => {
  const city = string.substring(0, string.indexOf(','));
  const state = string.substring((string.indexOf(',') + 2), (string.indexOf(',') + 4));
  const zip = string.substring((string.indexOf(state) + 3), string.length);
  return { city, state, zip };
};

const formatLocationObject = (string) => {
  /* eslint-disable camelcase */
  const location_name = string.substring(0, string.indexOf('\n'));
  const removedLocationName = string.substring((location_name.length + 1), string.length);
  const possibleAddress = removedLocationName.substring(0, removedLocationName.indexOf('\n'));
  let street_address;
  let cityStateZip;
  let phone;
  let hours_of_operation;
  if (possibleAddress.match(/^[0-9].*/)) {
    street_address = possibleAddress;
  }
  const removedPossibleAddress = removedLocationName
    .substring((possibleAddress.length + 1), removedLocationName.length);
  const possibleCity = removedPossibleAddress.substring(0, removedPossibleAddress.indexOf('\n'));

  if (possibleCity.match(/^[0-9].*/)) {
    street_address = possibleCity;
  }
  if (possibleCity.match(/^[A-Z].*/)) {
    cityStateZip = getCityStateZip(possibleCity);
  }
  const removedPossibleCity = removedPossibleAddress
    .substring((possibleCity.length + 1), removedPossibleAddress.length);

  const possiblePhone = removedPossibleCity.substring(0, removedPossibleCity.indexOf('\n'));
  if (possiblePhone.match(/^[0-9].*/)) {
    phone = formatPhoneNumber(possiblePhone);
  }
  if (possiblePhone.match(/^[A-Z].*/)) {
    cityStateZip = getCityStateZip(possiblePhone);
  }
  const removedPossiblePhone = removedPossibleCity
    .substring((possiblePhone.length + 1), removedPossibleCity.length);
  if (removedPossiblePhone.match(/^[0-9].*/)) {
    const phoneRaw = removedPossiblePhone.substring(0, removedPossiblePhone.indexOf('\n'));
    phone = formatPhoneNumber(phoneRaw);
    const removedPhone = removedPossiblePhone
      .substring((phone.length + 1), removedPossiblePhone.length);
    const hoursRaw = removedPhone.substring((removedPhone.indexOf('Hours') + 6), removedPhone.length);
    hours_of_operation = formatHours(hoursRaw);
  }
  if (removedPossiblePhone.match(/^[a-zA-z].*/)) {
    const hoursRaw = removedPossiblePhone.substring((removedPossiblePhone.indexOf('Hours') + 6), removedPossiblePhone.length);
    hours_of_operation = formatHours(hoursRaw);
  }
  return {
    location_name,
    street_address,
    ...cityStateZip,
    phone,
    hours_of_operation,
  };
};

const parseGoogleUrl = (string) => {
  if (!string) {
    return {
      latitude: undefined,
      longitude: undefined,
    };
  }
  if (!string.includes('@')) {
    return {
      latitude: undefined,
      longitude: undefined,
    };
  }
  const removedFiller = string.substring((string.indexOf('@') + 1), string.length);
  const geoArray = removedFiller.split(',');
  return {
    latitude: geoArray[0],
    longitude: geoArray[1],
  };
};

module.exports = {
  formatLocationObject,
  parseGoogleUrl,
};
