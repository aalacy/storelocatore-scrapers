const Apify = require('apify');
const axios = require('axios');

async function scrape() {
    stores = []
    let res = await axios.get('http://ocharleys.com/webapi/Locations?');
    let data = res.data;
    for(let store of data){
        let s = {
            locator_domain: 'http://ocharleys.com/',
            location_name: store.FriendlyName,
            street_address: store.Address,
            city: store.City,
            state: store.State,
            zip: store.Zip,
            country_code: 'US',
            store_number: store.StoreId,
            phone: store.MainPhone,
            location_type: store.CurbsideToGo,
            niacs_code: null,
            latitude: store.Latitude,
            longitude: store.Longitude,
            external_lat_long: false,
            hours_of_operation: null,
        }
        s.hours_of_operation = {
            'MonOpen': store.MonOpen,
            'MonClose': store.MonClose,
            'TueOpen': store.TueOpen,
            'TueClose': store.TueClose,
            'WedOpen': store.WedOpen,
            'WedClose': store.WedClose,
            'ThuOpen': store.ThuOpen,
            'ThuClose': store.ThuClose,
            'FriOpen': store.FriOpen,
            'FriClose': store.FriClose,
            'SatOpen': store.SatOpen,
            'SatClose': store.SatClose,
            'SunOpen': store.SunOpen,
            'SunClose': store.SunClose
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

