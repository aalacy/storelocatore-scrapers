const Apify = require('apify');
const axios = require('axios');

async function scrape() {
    stores = []
    let res = await axios.get('https://newbalance.locally.com/stores/conversion_data?has_data=true');
    //console.log(res.data.markers[369])
    for (let store of res.data.markers) {
        let s = {
            locator_domain: 'https://newbalance.locally.com/',
            location_name: store.name,
            street_address: store.address,
            city: store.city,
            state: store.state,
            zip: store.zip,
            country_code: store.country,
            store_number: store.id,
            phone: store.phone,
            location_type: null,
            niacs_code: null,
            latitude: store.lat,
            longitude: store.lng,
            external_lat_long: false,
            hours_of_operation: null
        }
        if(store.sun_time_open != 0 && store.mon_time_open != 0
        && store.wed_time_open != 0 && store.fri_time_open != 0){
            s.hours_of_operation = {
                sun_time_open: store.sun_time_open,
                sun_time_close: store.sun_time_close,
                mon_time_open: store.mon_time_open,
                mon_time_close: store.mon_time_close,
                tue_time_open: store.tue_time_open,
                tue_time_close: store.tue_time_close,
                wed_time_open: store.wed_time_open,
                wed_time_close: store.wed_time_close,
                thu_time_open: store.thu_time_open,
                thu_time_close: store.thu_time_close,
                fri_time_open: store.fri_time_open,
                fri_time_close: store.fri_time_close,
                sat_time_open: store.sat_time_open,
                sat_time_close: store.sat_time_close
            }
        }
        stores.push(s);
    }
    return stores;

}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

