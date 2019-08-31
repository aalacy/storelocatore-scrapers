const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

function insert(main_string, ins_string, pos) {
    if (typeof (pos) == "undefined") {
        pos = 0;
    }
    if (typeof (ins_string) == "undefined") {
        ins_string = '';
    }
    return main_string.slice(0, pos) + ins_string + main_string.slice(pos);
}

async function scrape() {

    var response = await axios.get('http://zacksfashions.com/?sm-xml-search=1&lat=43.6534829&lng=-79.38409389999998&radius=1000&namequery=43.653226,%20-79.3831843&query_type=all&limit=500&sm_category=&sm_tag=&address=&city=&state=&zip=&pid=16');

    var stores = response.data.map(store => ({
        locator_domain: 'zacksfashions.com',
        location_name: store.name,
        street_address: store.address + ' ' + store.address2,
        city: store.city,
        state: store.state,
        zip: store.zip.indexOf(' ') > 0 ? store.zip.trim() : insert(store.zip, ' ', 3).trim(),
        country_code: store.country,
        store_number: store.ID,
        phone: store.phone,
        location_type: store.taxes.sm_category,
        latitude: parseFloat(store.lat),
        longitude: parseFloat(store.lng),
        hours_of_operation: '<MISSING>',
    }));


    return stores;

}
