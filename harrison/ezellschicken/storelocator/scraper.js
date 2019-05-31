const Apify = require('apify');
const axios = require('axios');
const cheerio = require('cheerio');

async function scrape() {
    stores = []
    let res = await axios.get('https://www.ezellschicken.com/page/locations');
    const $ = cheerio.load(res.data);
    let locations = $('ol.locations');
    let loc = locations.find('li');
    while(loc.html() != null){
        console.log(loc.html());
        let s = {
            locator_domain: 'https://www.ezellschicken.com/',
            location_name: loc.find('h3').text(),
            street_address: loc.text(),
            city: loc.text()[2],
            state: loc.find('#text'),
            zip: null,
            country_code: null,
            store_number: null,
            phone: loc.find('strong').contents()[1].data,
            location_type: null,
            niacs_code: null,
            latitude: null,
            longitude: null,
            external_lat_long: true,
            hours_of_operation: loc.find('.hours').next().text()
        }
        stores.push(s);
        loc = loc.next();
    }

    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    console.log(data);
    //await Apify.pushData(data);
});


