//Author: Harrison Hayes
const Apify = require('apify');
const axios = require('axios');
const _ = require('underscore');

const states = require('./states.json');

function addIfNotInList(obj, list) {
    var doesNotExist = _.every(list, function(item) {
        return !_.isEqual(item, obj);
    });
    if (doesNotExist) {
        list.push(obj);
    }
}

async function scrape() {
    stores = [];
    for(let lat = -90; lat <= 90; lat+=30){
        for(let lon = -180; lon <= 180; lon+=30){
            console.log(stores)
            console.log('Scraping : ' + lat + ' ' + lon)
            //request gets 300 closest locations to geolocation...
            //Theres only ~167 US stores on 5/31/2019.
            let res = await axios.get('https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=stevemadden.myshopify.com&latitude='+lat+'&longitude='+lon+'&max_distance=0&limit=100000&calc_distance=1');
            for (let store of res.data.stores) {
                let s = {
                    locator_domain: 'https://stores.boldapps.net/',
                    location_name: store.name,
                    street_address: store.address,
                    city: store.city,
                    state: store.state,
                    zip: store.zip,
                    country_code: store.country,
                    store_number: store.store_id,
                    phone: store.phone,
                    location_type: null,
                    niacs_code: null,
                    latitude: store.lat,
                    longitude: store.lng,
                    external_lat_long: false,
                    hours_of_operation: null
                };
                if(store.prov_state == '') {
                    s.state = null;
                } else {
                    s.state = states[store.prov_state];
                }
                addIfNotInList(s, stores);
            }
        }
    }
    return stores;

}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

