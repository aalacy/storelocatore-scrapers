const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

async function scrape() {

    var response = await axios.get('https://federicosmexicanfood.com/wp-admin/admin-ajax.php?action=csl_ajax_onload&max_results=1000&autoload=1');

    if(response.success === false) {
        throw new Error("federicosmexicanfood API returened error. Try re-running.");
    }

    var stores = response.data.response.map(store => ({
        locator_domain: 'federicosmexicanfood.com',
        location_name: store.name.replace('&#039;', '\''),
        street_address: store.address + ' ' +store.address2,
        city: store.city,
        state: store.state,
        zip: store.zip,
        country_code: 'US',
        store_number: store.id,
        phone: store.phone,
        location_type: store.name.replace('&#039;', '\''),
        latitude: parseFloat(store.lat),
        longitude: parseFloat(store.lng),
        hours_of_operation: store.hours.replace('\\r\\n', ' '),
    }));


    return stores;

}
