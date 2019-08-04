const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

async function scrape() {

    var response = await axios.get('https://www.mobyskabob.com/wp-admin/admin-ajax.php?action=store_search&max_results=1000&autoload=1');

    var stores = response.data.map(store => ({
        locator_domain: 'mobyskabob.com',
        location_name: store.store,
        street_address: store.address + ' ' +store.address2,
        city: store.city,
        state: store.state,
        zip: store.zip,
        country_code: 'US',
        store_number: store.id,
        phone: store.phone,
        location_type: store.store,
        latitude: parseFloat(store.lat),
        longitude: parseFloat(store.lng),
        hours_of_operation: store.hours.replace(/<[^>]*>?/gm, ' '),
    }));


    return stores;

}
