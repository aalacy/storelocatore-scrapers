const Apify = require('apify');
const cheerio = require('cheerio');
const axios = require('axios');
async function scrape() {
    let stores = [];
    let res = await axios.get('https://www.samsung.com/us/samsung-experience-store/locations/');
    const $ = cheerio.load(res.data);
    let stores_data_name = $('body div div div section:nth-child(4) div');
    stores_data_name.find('.info-component').each((i, e) => {
        try {
            let s = {
                locator_domain: 'https://samsung.com/',
                location_name: $(e).find('.info-component-header').text(),
                street_address: $(e).find('.title').text().split('\n')[0],
                city: $(e).find('.title').text().split('\n')[1].split(',')[0].replace(/\s/g, ''),
                state: $(e).find('.title').text().split('\n')[1].split(',')[1].replace(/\d|\s/g, ''),
                zip: $(e).find('.title').text().split('\n')[1].split(',')[1].replace(/\D|\s/g, ''),
                country_code: 'US',
                store_number: null,
                phone: $(e).find('.phone-number').text(),
                location_type: null,
                niacs_code: null,
                latitude: null,
                longitude: null,
                external_lat_long: true,
                hours_of_operation1: $(e).find('div.first-column div.column-content p:nth-child(4)').text(),
                hours_of_operation2: $(e).find('div.first-column div.column-content p:nth-child(5)').text(),
            }
            stores.push(s);
        }
        catch (e) { console.log(url) }
    });
    await Promise.all(stores);
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});


