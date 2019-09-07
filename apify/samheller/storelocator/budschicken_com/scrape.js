const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {
  return await axios({
    method: "GET", 
    url: "http://www.budschicken.com/wp-admin/admin-ajax.php?action=store_search&lat=26.715342&lng=-80.05337500000002&max_results=25&radius=5000&autoload=1"
  }).then((resp) => {
    records = [];
    for (let store of resp.data){
      records.push({
        locator_domain: 'budschicken.com',
        location_name: store.store,
        street_address: store.address,
        city: store.city,
        state: store.state,
        zip: store.zip,
        country_code: 'US',
        store_number: store.id,
        phone: store.phone,
        location_type: '<MISSING>',
        latitude: store.lat,
        longitude: store.lng,
        hours_of_operation: store.hours.replace(/<time>/g, ': ').replace(/<\/time>/g, ', ').replace(/<.*?>/g, ''),      
      })
    }
    return records;
  })
}
