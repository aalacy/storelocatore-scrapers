const Apify = require('apify');
const axios = require('axios');

async function scrape() {
    stores = []
    let res = await axios.get('https://api-prod-gfp-us-a.tillster.com/mobilem8-web-service/rest/storeinfo/distance?_=1559334498038&latitude=0&longitude=0&maxResults=999999&radius=999999&statuses=ACTIVE,TEMP-INACTIVE,ORDERING-DISABLED&tenant=gfp-us');
    for (let store of res.data.getStoresResult.stores) {
        stores.push({
            locator_domain: 'https://api-prod-gfp-us-a.tillster.com/',
            location_name: store.storeName,
            street_address: store.street,
            city: store.city,
            state: store.state,
            zip: store.zipCode,
            country_code: store.country,
            store_number: store.storeId,
            phone: store.phoneNumber,
            location_type: null,
            niacs_code: null,
            latitude: null,
            longitude: null,
            external_lat_long: true,
            hours_of_operation: null
        });
    }
    return stores;

}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

