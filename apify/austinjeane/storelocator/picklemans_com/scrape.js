const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

async function scrape() {

    var response = await axios.get('https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/1554/stores');

    var stores = response.data.stores.map(store => {
        var parts = store.address.split('<br>');
        var street = parts[0];
        var bottomLineParts = parts[1].trim().split(',');
        var city, state, zip = null;
        
        if (bottomLineParts.length === 3) {
            city = bottomLineParts[0];
            state = bottomLineParts[1].trim();
            zip = bottomLineParts[2].trim();
        } else {
            city = bottomLineParts[0];
            state = bottomLineParts[1].trim().split(' ')[0];
            zip = bottomLineParts[1].split(' ')[2];
        }

        var name = store.name.split('<bd1>').join('').split('</bd1>').join('').trim();

        return {
            locator_domain: 'picklemans.com',
            location_name: name,
            street_address: street,
            city: city,
            state: state,
            zip: zip,
            country_code: 'US',
            store_number: store.id,
            phone: store.phone,
            location_type: store.category || name,
            latitude: parseFloat(store.latitude),
            longitude: parseFloat(store.longitude),
            hours_of_operation: "<INACCESSIBLE>",
        }
    });


    return stores;

}
