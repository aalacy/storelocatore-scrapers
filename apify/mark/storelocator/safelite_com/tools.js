const MISSING = '<MISSING>';

const formatPhoneNumber = (string) => {
  if (!string) {
    return MISSING;
  }
  const number = string.replace(/\D/g, '');
  if (number.length < 8) {
    return MISSING;
  }
  if (number.length > 10) {
    return number.substring(0, 10);
  }
  return number;
};

const formatAddress = (addrStr) => {
  if (!addrStr) {
    return {
      street_address: MISSING,
      city: MISSING,
      state: MISSING,
      zip: MISSING,
      country_code: MISSING
    };
  }

  const cleaned = addrStr.trim().split(',');

  // check if store is mobile which doesn't have an address
  if (cleaned.length > 2) {
    const stateAndZip = cleaned.pop().trim()
    const city = cleaned.pop().trim()
    const street_address = cleaned.join(',').trim();
    const [state, zip] = stateAndZip.trim().split(' ').map(el => el.trim());
    const country_code = MISSING;
  
  return {
    street_address, city, state, zip, country_code
  }
} else {
    const [city, state] = cleaned;
    return {
      city: city.trim(),
      state: state.trim(),
      street_address: MISSING, 
      zip: MISSING, 
      country_code: MISSING
    }
  }
}

const formatHours = (string) => {
  const hoursTrimmed = string.trim();
  const removeTabsNewLine = hoursTrimmed.replace(/\t/g, '').replace(/\n/g, ', ');
  return removeTabsNewLine;
};

module.exports = {
  MISSING,
  formatPhoneNumber,
  formatAddress,
  formatHours,
};
