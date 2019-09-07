const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

async function scrape() {

    var response = await axios.get('https://beverlytire.com/MyInstallers/data?enteredLocation=&isShowCommercialLocation=0');

    var stores = response.data.map(store => ({
        locator_domain: 'beverlytire.com',
        location_name: store.company,
        street_address: store.address1 + ' ' +store.address2,
        city: store.city,
        state: store.state,
        zip: store.zip,
        country_code: store.zip.match(/[a-z]/i) ? 'CA' : 'US',
        store_number: store.id,
        phone: store.phone,
        location_type: store.company,
        latitude: parseFloat(store.latitude),
        longitude: parseFloat(store.longitude),
        hours_of_operation: store.hours.replace(/<[^>]*>?/gm, ' '),
    }));


    return stores;

}
