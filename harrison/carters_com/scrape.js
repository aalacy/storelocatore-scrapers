//Harrison Hayes
const Apify = require('apify');
const puppeteer = require('puppeteer');

async function scrape() {

    let stores = [];

    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
        defaultViewport: { width: 1920, height: 1080 },
    });
    const page = await browser.newPage();
    page.on('response', async response => {
        try {
            let data = await response.json();
            data = data.stores;
            for(let key in data){
                if(data[key].isOpen == 'open'){
                    let store = data[key];
                    await stores.push({
                        locator_domain: 'https://www.carters.com/',
                        location_name: store.name,
                        street_address: store.address1,
                        city: store.city,
                        state: store.stateCode,
                        zip: store.postalCode,
                        country_code: store.countryCode,
                        store_number: store.storeid,
                        phone: store.phone,
                        location_type: null,
                        niacs_code: null,
                        latitude: store.latitude,
                        longitude: store.longitude,
                        external_lat_long: false,
                        hours_of_operation: {
                            'Sunday Hours': store.sundayHours,
                            'Monday Hours': store.mondayHours,
                            'Tuesday Hours': store.tuesdayHours,
                            'Wednesday Hours': store.wednesdayHours,
                            'Thurday Hours': store.thursdayHours,
                            'Friday Hours': store.fridayHours,
                            'Saturday Hours': store.saturdayHours,
                        },
                    });
                }
            }
        } catch(err) {
            console.log('Try again later, encountered CAPTCH.');
        }
    });
    await page.goto('https://www.carters.com/on/demandware.store/Sites-Carters-Site/default/Stores-GetNearestStores?carters=true&oshkosh=false&skiphop=false&lat=0&lng=0');
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

