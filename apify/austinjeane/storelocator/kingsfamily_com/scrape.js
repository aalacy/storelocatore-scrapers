const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

async function scrape() {

    var response = await axios.get('https://www.kingsfamily.com/wp-admin/admin-ajax.php?action=asl_load_stores&load_all=1&layout=1');

    var stores = response.data.map(store => ({
        locator_domain: 'kingsfamily.com',
        location_name: store.title,
        street_address: store.street,
        city: store.city,
        state: store.state,
        zip: store.postal_code,
        country_code: 'US',
        store_number: store.id,
        phone: store.phone,
        location_type: store.title,
        latitude: parseFloat(store.lat),
        longitude: parseFloat(store.lng),
        hours_of_operation: store.open_hours.replace(/\"/g, "").split(",").join(" ").split("{").join("").split("}").join("").split("[").join("").split("]").join("")
    }));


    return stores;

}
