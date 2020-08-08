const Apify = require('apify');
const axios = require('axios');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

function formatHoursOfOperation(serializedHours) {
  const REPLACE_OPEN_BRACKET_REGEX = /\[/g;
  const REPLACE_CLOSE_BRACKET_REGEX = /\]/g;
  const REMOVE_TRAILING_COLON_REGEX = /,$/;
  const REMOVE_SECONDS_REGEX = /\:\d\d$/;

  const cleaned = serializedHours
    .replace(REPLACE_OPEN_BRACKET_REGEX, '{')
    .replace(REPLACE_CLOSE_BRACKET_REGEX, '},')
    .replace(REMOVE_TRAILING_COLON_REGEX, '');

  const data = JSON.parse(`[${cleaned}]`);
  const hours = data.map((day) => ({
    day: day.Interval,
    open: day.OpenTime.replace(REMOVE_SECONDS_REGEX, ''),
    close: day.CloseTime.replace(REMOVE_SECONDS_REGEX, ''),
  }));

  return hours.length ? JSON.stringify(hours) : null;
}

Apify.main(async () => {
  const urlLocation = 'https://www.sweetandsassy.com/locations/?CallAjax=GetLocations';
  const { data } = await axios.post(urlLocation);

  const pois = data.map((location) => {
    return {
      locator_domain: 'sweetandsassy.com',
      page_url: urlLocation,
      location_name: getOrDefault(location.FranchiseLocationName),
      store_number: getOrDefault(location.FranchiseLocationID),
      street_address: getOrDefault(location.Address1),
      city: getOrDefault(location.City),
      state: getOrDefault(location.State),
      zip: getOrDefault(location.ZipCode),
      country_code: getOrDefault(location.Country),
      latitude: getOrDefault(location.Latitude),
      longitude: getOrDefault(location.Longitude),
      phone: getOrDefault(location.Phone),
      hours_of_operation: getOrDefault(formatHoursOfOperation(location.LocationHours)),
      location_type: MISSING,
    };
  });

  await Apify.pushData(pois);
});
