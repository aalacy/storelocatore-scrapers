const Apify = require('apify');
const axios = require('axios');

async function scrape() {
    stores = []
    let res = await axios.get('https://locations.pon-bon.com/locations.json');
    let data = res.data.locations;
    for(let store of data){
        s = {
            locator_domain: 'https://locations.pon-bon.com/',
            location_name: store.loc.name,
            street_address: store.loc.address1,
            city: store.loc.city,
            state: store.loc.state,
            zip: store.loc.postalCode,
            country_code: 'US',
            store_number: store.loc.id,
            phone: store.loc.phone,
            location_type: store.loc.type,
            niacs_code: null,
            latitude: store.loc.latitude,
            longitude: store.loc.longitude,
            external_lat_long: false,
            hours_of_operation: null,
        }
        stores.push(s);
    }
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

