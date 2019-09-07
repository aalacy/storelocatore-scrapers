// Leaves only digits for the phone number
const formatPhoneNumber = (string) => {
  const number = string.replace(/\D/g, '');
  if (number.length === 0) {
    return undefined;
  }
  if (number.length > 10) {
    return number.substring(0, 9);
  }
  return number;
};

const parseGoogleMapsUrl = (string) => {
  if (typeof (string) !== 'string') {
    return undefined;
  }
  const a = string.match(/(?=)([-]?[\d]*\.[\d]*),([-]?[\d]*\.[\d]*)(?=&)/g);
  const s = a[0];
  const o = s.split(',');
  return {
    latitude: o[0],
    longitude: o[1],
  };
};

const formatStreetAddress = (string1, string2) => {
  if (typeof (string2) === 'string') {
    if (string2.length === 0) {
      return string1;
    }
    return `${string1}, ${string2}`;
  }
  return string1;
};

const parseAddress = (a) => {
  if (typeof (a) !== 'string') {
    return undefined;
  }
  const r = {};
  const c = a.indexOf(',');
  r.city = a.slice(0, c);
  const f = a.substring(c + 2);
  const s = f.lastIndexOf(' ');
  r.state = f.slice(0, s);
  r.zip = f.substring(s + 1);
  return r;
};

const checkLocationType = (url) => {
  if (url.includes('branch')) {
    return 'Branch';
  }
  if (url.includes('office')) {
    return 'Office';
  }
  if (url.includes('atm')) {
    return 'ATM';
  }
  return undefined;
};

const checkHours = (string) => {
  if (string.length === 0) {
    return undefined;
  }
  return string;
};

module.exports = {
  formatPhoneNumber,
  parseGoogleMapsUrl,
  formatStreetAddress,
  parseAddress,
  checkLocationType,
};
