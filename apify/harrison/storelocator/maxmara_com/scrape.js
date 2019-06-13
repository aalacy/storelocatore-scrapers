//Harrison Hayes
const Apify = require('apify');
const axios = require('axios');

async function scrape() {
    stores = []
    let res = await axios.get('https://us.maxmara.com/store-locator?south=-99999999&west=-99999999&north=99999999&east=99999999&lat=0&lng=0&name=&listJson=true');
    let data = res.data.features;
    for(let store of data){
        let s = {
            locator_domain: 'https://us.maxmara.com/',
            location_name: store.properties.displayName,
            street_address: null,
            city: store.properties.city,
            state: null,
            zip: store.properties.zip,
            country_code: null,
            store_number: null,
            phone: store.properties.phone1,
            location_type: null,
            niacs_code: null,
            latitude: store.properties.lat,
            longitude: store.properties.lng,
            external_lat_long: false,
            hours_of_operation: null,
        }
        let prov;
        if(store.properties.prov) {
            prov = store.properties.prov;
            s.country_code = prov.substring(0, 2);
            s.state = prov.substring(prov.length-2, prov.length);
        }
        s.street_address = store.properties.formattedAddress.replace(s.city, '')
            .replace(s.zip, '').split(',');
        for(let i = 0; i < s.street_address.length; i++){
            if(!s.street_address[i].match(/[A-Za-z0-9]/)){
                s.street_address.splice(i, 1);
            }
        }
        s.street_address = s.street_address.join('');
        stores.push(s);
    }
    //console.log(stores);
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

