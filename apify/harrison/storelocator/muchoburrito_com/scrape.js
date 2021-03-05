const Apify = require('apify');
const axios = require('axios');

async function scrape() {
  const params = {
    auth_token: 'GTKDWXDZMLHWYIKP',
    multi_account: false,
    pageSize: 10000,
  };
  let res = await axios.get('https://api.momentfeed.com/v1/analytics/api/llp.json', {
    params,
  });
  let data = res.data;

  const locations = [];
  for (let store of data) {
    let s = {
      locator_domain: 'https://momentfeed-prod.apigee.net/',
      page_url: store.store_info.website,
      location_name: store.store_info.name,
      street_address: store.store_info.address,
      city: store.store_info.locality,
      state: store.store_info.region,
      zip: store.store_info.postcode,
      country_code: store.store_info.country,
      store_number: store.store_info.corporate_id,
      phone: store.store_info.phone,
      location_type: '<MISSING>',
      latitude: store.store_info.latitude,
      longitude: store.store_info.longitude,
      hours_of_operation: formatHours(store.store_info.hours),
    };
    locations.push(s);
  }

  return locations;
}

function formatHours(hours) {
  const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
  let res = [];
  for (let hour of hours.split(';')) {
    const parts = hour.split(',');
    if (parts.length == 3) {
      const day = parseInt(parts[0]) - 1;
      const dayName = days[day];
      const open = parts[1];
      const close = parts[2];
      res.push(dayName + ': ' + open + '-' + close);
    }
  }
  return res.join(', ');
}

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});
