//Harrison Hayes
const Apify = require('apify');
const puppeteer = require('puppeteer');

async function scrape() {

    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
        defaultViewport: { width: 1920, height: 1080 },
    });
    const page = await browser.newPage();
    await page.goto('https://www.thejerkyoutlet.com/locations', { waituntil: 'load' });
    const stores = await page.$$eval(
        '#content > div.locations-div > div > div',
        elements => {
            let stores = [];
            for (const e of elements) {
                let text = e.textContent;
                const store_obj = {
                    locator_domain: 'https://www.thejerkyoutlet.com/',
                    location_name: null,
                    street_address: null,
                    city: null,
                    state: null,
                    zip: null,
                    country_code: 'US',
                    store_number: null,
                    phone: null,
                    location_type: null,
                    niacs_code: null,
                    latitude: null,
                    longitude: null,
                    external_lat_long: true,
                    hours_of_operation: null,
                };
                store_obj.street_address = e.innerText.split('\n')[0];
                store_obj.zip = e.innerText.split('\n')[1].substring(e.innerText.split('\n')[1].length-5, e.innerText.split('\n')[1].length);
                store_obj.state = e.innerText.split('\n')[1].substring(e.innerText.split('\n')[1].length-8, e.innerText.split('\n')[1].length-6);
                store_obj.city = e.innerText.split('\n')[1].substring(0, e.innerText.split('\n')[1].length-9).replace(',', '');
                store_obj.phone = e.innerText.split('\n')[2].replace(/\D/g, '');
                stores.push(store_obj);
            }
            return stores;
        }
    );
    //console.log(stores);
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});
