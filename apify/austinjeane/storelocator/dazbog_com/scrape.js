const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

function stripHtml(html) {
    return html
        .replace(/<[^>]*>?/gm, ' ') //remove hmtl
        .replace(/ +(?= )/g, ''); // replace multiple spaces with one space
}

async function scrape() {

    var response = await axios.get('https://dazbog.com/wp-admin/admin-ajax.php?action=store_search&max_results=1000&autoload=1');

    //api is returning 2 addresses with same lat/lng
    var existingLatitudeLongitudePairs = {};

    var stores = response.data.map(store => {
        var lat = '<MISSING>';
        var lng = '<MISSING>';
        if(existingLatitudeLongitudePairs[store.lat+store.lng] == null) {
            existingLatitudeLongitudePairs[store.lat+store.lng] = true;
            lat = parseFloat(store.lat);
            lng = parseFloat(store.lng);
        }
        return {
            locator_domain: 'dazbog.com',
            location_name: store.store,
            street_address: store.address + ' ' + store.address2,
            city: store.city,
            state: store.state,
            zip: store.zip,
            country_code: 'US',
            store_number: store.id,
            phone: store.phone,
            location_type: store.store,
            latitude: lat,
            longitude: lng,
            hours_of_operation: stripHtml(store.hours),
        };
    });


    return stores;

}
