//Harrison Hayes
const Apify = require('apify');
const axios = require('axios');

const states = require('./states.json');

async function scrape() {
    stores = []
    let res = await axios.get('http://www.lowesfoods.com/lfs/components/remoteProxy.cfc?method=returnStoresByLocation&latitude=0&longitude=0&radius=9999999');
    let data = res.data.stores.DATA;
    for(let i = 0; i < res.data.stores.ROWCOUNT; i+=1){
        stores.push({
            locator_domain: 'http://www.lowesfoods.com/',
            location_name: data.STORE_DISPLAY_NAME[i],
            street_address: data.STORE_ADDRESS1[i],
            city: data.STORE_CITY[i],
            state: states[data.STORE_STATE[i]],
            zip: data.STORE_ZIP[i],
            country_code: 'US',
            store_number: data.STORE_NUMBER[i],
            phone: data.STORE_PHONE[i],
            location_type: data.STORE_AMENITIES[i].split(','),
            niacs_code: null,
            latitude: data.LATITUDE[i],
            longitude: data.LONGITUDE[i],
            external_lat_long: false,
            hours_of_operation: data.STORE_HOURS[i],
        });
    }
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

