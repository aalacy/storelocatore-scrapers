//Harrison Hayes
const Apify = require('apify');
const axios = require('axios');

async function scrape() {
    stores = []
    let res = await axios.get('https://momentfeed-prod.apigee.net/api/llp.json?auth_token=GTKDWXDZMLHWYIKP&pageSize=9999999');
    let data = res.data;
    for(let store of data){
        let s = {
            locator_domain: 'https://momentfeed-prod.apigee.net/',
            location_name: store.store_info.name,
            street_address: store.store_info.address,
            city: store.store_info.locality,
            state: store.store_info.providers.facebook_region,
            zip: store.store_info.postal_code,
            country_code: store.store_info.country,
            store_number: store.store_info.corporate_id,
            phone: store.store_info.phone,
            location_type: null,
            niacs_code: null,
            latitude: store.store_info.latitude,
            longitude: store.store_info.longitude,
            external_lat_long: false,
            // ****Order of hours array is order of days in         ****
            // ****week. Unsure if it starts on sunday or monday.   ****
            hours_of_operation: store.store_info.hours.split(';'),
        }
        for(let i = 0; i < s.hours_of_operation.length; i++){
            s.hours_of_operation[i] = s.hours_of_operation[i].split(',').splice(1, 2);
        }
        if(s.hours_of_operation.length > 7){
            s.hours_of_operation.pop();
        }
        stores.push(s);
    }
    //console.log(stores);
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

