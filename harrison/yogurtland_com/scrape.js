//Harrison Hayes
const Apify = require('apify');
const cheerio = require('cheerio');
const axios = require('axios');

async function get_location_data(url) {

    try {
        let res = await axios.get(url);
        const $ = cheerio.load(res.data);
        let store_data = cheerio.load($('.store-data > div').html());
        let s = {
            locator_domain: 'https://www.yogurt-land.com/',
            location_name: store_data('.storeData-name').text().replace('\n', ''),
            street_address: store_data('.storeData-address').text().split('\n')[1],
            city: store_data('.storeData-address').text().split('\n')[2].split(',')[0],
            state: store_data('.storeData-address').text().split('\n')[2].split(',')[1].replace(' ', ''),
            zip: store_data('.storeData-address').text().split('\n')[3].split(' ')[0],
            country_code: store_data('.storeData-address').text().split('\n')[3].split(' ')[1],
            store_number: null,
            phone: store_data('.storeData-contact').text().replace(/\D/g, ''),
            location_type: null,
            niacs_code: null,
            latitude: null,
            longitude: null,
            external_lat_long: true,
            hours_of_operation: store_data('ol.store-hours-list').text().split('\n'),
        }
        let hours = {}
        for (let i = 0; i < s.hours_of_operation.length; i++) {
            if (s.hours_of_operation[i].charAt(0) == 'S' ||
                s.hours_of_operation[i].charAt(0) == 'M' ||
                s.hours_of_operation[i].charAt(0) == 'T' ||
                s.hours_of_operation[i].charAt(0) == 'W' ||
                s.hours_of_operation[i].charAt(0) == 'F') {
                hours[s.hours_of_operation[i]] = s.hours_of_operation[i+1];
            }
        }
        s.hours_of_operation = hours;
        return s
    } catch(err) {
        //catches the out of country stores that have different layouts
    }
}

async function scrape() {

    stores = [];

    let res = await axios.get('https://www.yogurt-land.com/site_maps/index.xml');
    const $ = await cheerio.load(res.data);
    let links = await $('loc');
    for (let i = 0; i < links.length; i++) {
        if($(links[i]).text().includes('https://www.yogurt-land.com/locations/')) {
            stores.push(get_location_data($(links[i]).text()));
        }
    }
    await Promise.all(stores);
    console.log(stores.length);
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});
