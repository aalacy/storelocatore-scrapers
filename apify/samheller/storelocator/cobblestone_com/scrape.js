const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  return await axios({
    method: 'GET',
    url: 'https://cobblestone.com/?sm-xml-search=1&lat=33.4483771&lng=-112.07403729999999&radius=0&namequery=33.4483771%2C%20-112.07403729999999&query_type=all&limit=0&sm_category&locname&address&city&state&zip&pid=260'
  }).then((resp) => {
    data = [];
    for (let row of resp.data){
      data.push({
        locator_domain: 'cobblestone.com',
        location_name: row.post_title.replace('(Express)', ''),
        street_address: row.address,
        city: row.city,
        state: row.state,
        zip: row.zip,
        country_code: 'US',
        store_number: row.ID,
        phone: row.phone,
        location_type: row.post_title.startsWith('(Express)') ? 'Express' : 'Normal',
        latitude: row.lat,
        longitude: row.lng,
        hours_of_operation: '<MISSING>',
      })            
    }
    return data;
  })

}

