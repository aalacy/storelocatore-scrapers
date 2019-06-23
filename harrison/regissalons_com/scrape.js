//Harrison Hayes
const Apify = require('apify');
const cheerio = require('cheerio');
const axios = require('axios');

async function get_location_data(url) {
    try{
    let res = await axios.get(url);
    const $ = cheerio.load(res.data);
    let store_data = $('.tbg-column');
    let s = {
        locator_domain: 'https://www.regissalons.com/',
        location_name: $(store_data).find('h2').text(),
        street_address: null,
        city: null,
        state: null,
        zip: null,
        country_code: null,
        store_number: null,
        phone: $(store_data).find('a').text().replace(/\D/g, ''),
        location_type: null,
        niacs_code: null,
        latitude: null,
        longitude: null,
        external_lat_long: true,
        hours_of_operation: null,
    }
    let address = $(store_data).find('address').text().replace(/\t/g, '').split('\n');
    s.street_address = address[1];
    s.city = address[2].split(' ')[0];
    s.state = address[2].split(' ')[1];
    s.zip = address[2].split(' ')[2];
    s.country_code = address[3].substring(0, 2);
    //console.log('DONE:' + url);
    return s;
    } catch(err){
        // print the URL if network error occured
        console.log(url);
    }
}

async function scrape() {

    stores = [];

    let res = await axios.get('https://www.regissalons.com/wpsl_stores-sitemap.xml');
    const $ = await cheerio.load(res.data);
    let links = await $('loc');
    for (let i = 0; i < links.length; i++) {
        stores.push(await get_location_data($(links[i]).text()));
    }
    //await Promise.all(stores);
    //console.log(stores.length);
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});
