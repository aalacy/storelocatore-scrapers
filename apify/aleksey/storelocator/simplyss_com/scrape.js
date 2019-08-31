const Apify = require('apify');
const cheerio = require('cheerio');
const axios = require('axios');

async function get_states() {
    let states = [];
    let res = await axios.get('https://www.simplyss.com/locations/?a=map');
    const $ = cheerio.load(res.data);
    let states_data = $('.home-search-by-city-row');
    let states_data1 = states_data.find('.column');
    let states_data2 = states_data1.find('a').text().split(' Self Storage');
    states = states_data2;
    return states;
}

async function get_urls() {
    let urls = [], data = [];
    data = await get_states();
    for (let i = 0; i < data.length - 1; i++) {
        urls[i] = 'https://www.simplyss.com/' + data[i].replace(' ', '-') + '/';
    }
    return urls;
}

async function scrape() {
    let stores = [];
    let stores_all_num = 0;
    let stores_all_num_pre = 0;
    let stores_address = [];
    let stores_name = [];
    let stores_phone = [];
    let stores_city = [];
    let stores_zip = [];
    const states = await get_states();
    let stores_states = [];
    const urls = await get_urls();
    for (let i = 0; i < urls.length; i++) {
        let res = await axios.get(urls[i]);
        const $ = cheerio.load(res.data);
        let instate_stores_num1 = $('body div div div.locations-rows-container div div.loc-details-box div div.theme-dark-blue');
        let instate_stores_num2 = instate_stores_num1.text();
        instate_stores_num = instate_stores_num2.length;
        if (instate_stores_num > 28) {
            instate_stores_num = (instate_stores_num + 9) / 4;
        } else {
            instate_stores_num = instate_stores_num / 3
        }
        stores_all_num = stores_all_num + instate_stores_num;
        stores_all_num_pre = stores_all_num - instate_stores_num;
        let stores_address_temp = [];
        let stores_name_temp = [];
        let stores_phone_temp = [];
        let stores_city_temp = [];
        let stores_city_tt = [];
        for (let j = stores_all_num_pre; j < stores_all_num; j++) {
            let jj = (j - stores_all_num_pre) * 2 + 1;
            let stores_data = $('body div div div.locations-rows-container div:nth-child(' + jj + ') div.loc-details-box div div');
            stores_address[j] = stores_data.find('.address .visible-lg').text();
            stores_states[j] = states[i];
            stores_phone[j] = stores_data.find('.phone-email').text().replace(/\D/g, '');
            stores_city_tt[j] = stores_data.find('.address').text();
            stores_name[j] = stores_city_tt[j].split(',')[0];
            if (j > stores_all_num_pre) {
                stores_address_temp = stores_address_temp + stores_address[j];
                stores_name_temp = stores_name_temp + stores_name[j];
                stores_phone_temp = stores_phone_temp + stores_phone[j];
                stores_city_temp = stores_city_temp + stores_city_tt[j];
            }
        }
        stores_address[stores_all_num_pre] = stores_address[stores_all_num_pre].replace(stores_address_temp, '');
        stores_name[stores_all_num_pre] = stores_name[stores_all_num_pre].replace(stores_name_temp, '');
        stores_phone[stores_all_num_pre] = stores_phone[stores_all_num_pre].replace(stores_phone_temp, '');
        stores_city_tt[stores_all_num_pre] = stores_city_tt[stores_all_num_pre].replace(stores_city_temp, '');
        for (let j = stores_all_num_pre; j < stores_all_num; j++) {
            stores_city[j] = stores_city_tt[j].split(',')[1].split(' ')[1];
            stores_zip[j] = stores_city_tt[j].split(',')[1].replace(/\D/g, '');
            stores_name[j] = stores_name[j].replace(/\n/g,'#').split('#')[5];
        }
            }
    try {
        for (let mm = 0; mm < stores_all_num; mm++) {
            let s = {
                locator_domain: 'https://www.simplyss.com/',
                location_name: stores_name[mm],
                street_address: stores_address[mm],
                city: stores_city[mm],
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



