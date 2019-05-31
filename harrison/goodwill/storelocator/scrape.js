const Apify = require('apify');
const axios = require('axios');


const services = ['Retail', 'Job Support', 'Donation Site', 'Outlet', 'Headquarters'];
const countries = {'Canada': 'CA', 'United States': 'US', 'Venezuela': 'VE', 'Trinidad and Tobago': 'TT'}

async function get_store(store_num) {
    try {
        let res = await axios.get('http://www.goodwill.org/?faster_ajax=1&action=gii_locator_get_location&id='+store_num);
        let store = res.data;
        s = {
            locator_domain: 'http://www.goodwill.org/',
            location_name: store.name,
            street_address: store.address1,
            city: store.city,
            state: store.state,
            zip: store.postal_code,
            country_code: countries[store.country],
            store_number: store.id,
            phone: store.phone,
            location_type: [],
            niacs_code: null,
            latitude: store.lat,
            longitude: store.lng,
            external_lat_long: false,
            hours_of_operation: null,
        }
        for(let service of store.services) {
           s.location_type.push(services[service]);
        }
        console.log(store_num);
        return s;
    } catch(err) {
        console.log(err);
        console.log('Store Failed: ' + store_num);
    }
}

async function scrape() {
    stores = []
    let res = await axios.get('http://www.goodwill.org/?action=gii_locator_locations&points_only=1&lat=&lng=&faster_ajax=1');
    let num_stores = res.data.length;

    for(let i = 1; i <= num_stores; i++) {
        stores.push(get_store(i));
    }
    stores = await Promise.all(stores);
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

