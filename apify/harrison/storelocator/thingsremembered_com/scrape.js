const Apify = require('apify');
const axios = require('axios');

async function scrape() {
    stores = []
    let res = await axios.get('https://www.thingsremembered.com/storelocator/stores.json');
    let data = res.data;
    for(let store of data){
        stores.push({
            locator_domain: 'https://www.thingsremembered.com/',
            location_name: store.name,
            street_address: store.address1,
            city: store.city,
            state: store.stateAddress,
            zip: store.postalCode,
            country_code: 'US',
            store_number: store.locationId,
            phone: store.phoneNumber,
            location_type: null,
            niacs_code: null,
            latitude: store.latitude,
            longitude: store.longitude,
            external_lat_long: false,
            hours_of_operation: store.hours,
        });
    }
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

