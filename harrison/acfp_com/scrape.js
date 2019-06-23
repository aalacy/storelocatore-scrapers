//Harrison Hayes
const Apify = require('apify');
const cheerio = require('cheerio');
const axios = require('axios');

async function get_location_data(url) {

    let store = [];

    let res = await axios.get(url);
    const $ = cheerio.load(res.data);
    let stores_data = $('.inside');

    stores_data.find('.a-location').each((i, e) => {
        try{
        let s = {
            locator_domain: 'https://acfp.com/',
            location_name: $(e).find('.name').text().replace(/\d/g, ''),
            street_address: $(e).find('.address').text().split('\n')[0],
            city: $(e).find('.address').text().split('\n')[$(e).find('.address').text().split('\n').length-2].split(',')[0],
            state: $(e).find('.address').text().split('\n')[$(e).find('.address').text().split('\n').length-2].split(',')[1].replace(/\d|\s/g, ''),
            zip: $(e).find('.address').text().split('\n')[$(e).find('.address').text().split('\n').length-2].split(',')[1].replace(/\D|\s/g, ''),
            country_code: 'US',
            store_number: null,
            phone: $(e).find('.phone').text(),
            location_type: null,
            niacs_code: null,
            latitude: null,
            longitude: null,
            external_lat_long: true,
            hours_of_operation: $(e).find('.hours').text().replace(/\t/g, '').split('\n'),
        }
        let hours = {}
        for (let i = 0; i < s.hours_of_operation.length; i++) {
            if (s.hours_of_operation[i] == '') {
                s.hours_of_operation.splice(i, 1);
            }
        }
        stores.push(s);} catch(e){console.log(url)}
    });

    return stores;
}

async function scrape() {

    stores = [];

    let res = await axios.get('https://acfp.com/acfp_location_state-sitemap.xml');
    const $ = await cheerio.load(res.data);
    let links = await $('loc');
    for (let i = 0; i < links.length; i++) {
        stores.push(get_location_data($(links[i]).text()));
    }
    await Promise.all(stores);
    //console.log(stores);
    //console.log(stores.length);
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});
