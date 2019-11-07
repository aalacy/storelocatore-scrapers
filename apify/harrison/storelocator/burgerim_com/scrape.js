const Apify = require('apify');
const axios = require('axios');

async function scrape() {
    stores = []
    let res = await axios.get('https://www.burgerim.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=e151aba9dc&load_all=1&layout=1');
    let data = res.data;
    for(let store of data){
        if (store.categories != null){
            stores.push({
                locator_domain: 'https://www.burgerim.com/',
                location_name: store.title,
                street_address: store.street,
                city: store.city,
                state: store.state,
                zip: store.postal_code,
                country_code: 'US',
                store_number: store.id,
                phone: store.phone,
								location_type: '<MISSING>',
                latitude: store.lat,
                longitude: store.lng,
                hours_of_operation: store.open_hours,
            });
        }
    }
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

