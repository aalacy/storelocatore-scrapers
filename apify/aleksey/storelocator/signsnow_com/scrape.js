const Apify = require('apify');
const cheerio = require('cheerio');
const axios = require('axios');

async function get_stores_name() {
    let stores_name = [];
    let stores_all_num = 0;
    let stores_state_num = 0;
    let stores_all_pre = 0;
    let res = await axios.get('https://www.signsnow.com/all-locations');
    const $ = cheerio.load(res.data);
    for (let i = 1; i < 32; i++) {
        let states_data = $('body div:nth-child(3) div div div:nth-child(2) div.column45');
        let states_data1 = states_data.find('ul li:nth-child(' + i + ') ul li a').text().split(/Signs Now /g);
        stores_state_num = states_data1.length - 1;
        stores_all_num = stores_all_num + stores_state_num;
        stores_all_pre = stores_all_num - stores_state_num;
        for (let j = stores_all_pre + 1; j < stores_all_num + 1; j++) {
            let position = states_data1[j - stores_all_pre].indexOf('Image360');
            if (position != -1) {
                stores_name[j - 1] = states_data1[j - stores_all_pre].substring(0, position).split(/\(/g)[0].replace(/\W/g, '');
            } else {
                stores_name[j - 1] = states_data1[j - stores_all_pre].split(/\(/g)[0].replace(/\W/g, '');
            }
        }
    }
    return stores_name;
}

async function get_urls() {
    let urls = [], data = [];
    data = await get_stores_name();
    for (let i = 0; i < data.length - 1; i++) {
        urls[i] = 'https://www.signsnow.com/' + data[i].replace(/\s/g, '') + '/';
    }
    urls[13] = 'https://www.signsnow.com/orlandofl';
    urls[16] = 'https://www.signsnow.com/sunrise';
    urls[59] = 'https://www.signsnow.com/newark';
    return urls;
}

async function scrape() {
    let stores = [];
    let stores_address = [];
    let location_name = [];
    let stores_phone = [];
    let stores_zip = [];
    let stores_states = [];
    let stores_states1 = [];
    let stores_states2 = [];
    const urls = await get_urls();
    for (let i = 0; i < urls.length; i++) {
        let res = await axios.get(urls[i]);
        const $ = cheerio.load(res.data);
        stores_phone[i] = $('.phone').text().replace(' ', '');
        location_name[i] = urls[i].replace('https://www.signsnow.com/', '').replace(/\W/g, '');
        stores_address[i] = $('.contact').text().split(location_name[i])[0].split('Map')[1].replace('. ', '').split(',')[0];
        stores_states1[i] = $('.contact').text().split(',');
        let contact_num = stores_states1[i].length;
        stores_states2[i] = stores_states1[i][contact_num - 1];
        stores_states[i] = stores_states2[i].replace(/\W/g, '').replace(/\d/g, '');
        stores_zip[i] = stores_states2[i].replace(/\W/g, '').replace(/\D/g, '');
    }

    try {
        for (let mm = 0; mm < urls.length; mm++) {
            let s = {
                locator_domain: 'https://www.signsnow.com/',
                location_name: location_name[mm],
                street_address: stores_address[mm],
                city: null,
                state: stores_states[mm],
                zip: stores_zip[mm],
                country_code: 'US',
                store_number: null,
                phone: stores_phone[mm],
                location_type: null,
                niacs_code: null,
                latitude: null,
                longitude: null,
                external_lat_long: true,
                hours_of_operation: null,
            }
            stores.push(s);
        }
    }
    catch (error) { console.log(error) }
    await Promise.all(stores);
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});



