const Apify = require('apify');
const request = require('request-promise');

const MISSING = '<MISSING>';

function getOrDefault(value) {
  if (Array.isArray(value)) {
    return value.length ? JSON.stringify(value) : MISSING;
  }

  return value || MISSING;
}

function parseHours(hours) {
  return hours.map((day) => ({
    start: day.close ? '' : day.start,
    end: day.close ? '' : day.end,
    day: day.label_en,
  }));
}

Apify.main(async () => {
  const response = await request.get('https://www.bumpertobumper.ca/json/stores.json');
  data = JSON.parse(response);

  const records = data.map((garage) => {
    const {
      city,
      phone,
      country,
      hours,
      region: state,
      id: store_number,
      name: location_name,
      address: street_address,
      postal_code: zip,
      garage_type: location_type,
      lat: latitude,
      long: longitude,
    } = garage;

    const poi = {
      locator_domain: 'bumpertobumper.ca',
      city: getOrDefault(city),
      phone: getOrDefault(phone.replace(/-/g, '')),
      location_name: getOrDefault(location_name),
      street_address: getOrDefault(street_address),
      state: getOrDefault(state),
      zip: getOrDefault(zip),
      store_number: getOrDefault(store_number),
      location_type: getOrDefault(location_name),
      latitude: getOrDefault(latitude),
      longitude: getOrDefault(longitude),
      store_number: getOrDefault(store_number),
      hours_of_operation: getOrDefault(parseHours(hours)),
      country_code: country.match(/canada/i) ? 'CA' : country,
    };

    return poi;
  });

  await Apify.pushData(records);
});
