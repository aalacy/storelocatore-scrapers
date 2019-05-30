const puppeteer = require('puppeteer');
const program = require('commander');

const { Store } = require('./store.js');
const { Stores } = require('./store.js');
const { NO_DATA } = require('./store.js');

function makeStore(store) {
  const locator_domain = 'www.shopnsavefood.com';
  const locator_name = store.Name;
  const address = store.Address1;
  const city = store.City;
  const state = store.State;
  const zip = store.Zip;
  const country_code = 'US';
  const store_number = store.StoreID;
  const phone = store.Phone;
  const location_type = NO_DATA;
  const naics_code = NO_DATA;
  const latitude = store.Latitude;
  const longitude = store.Longitude;
  const external_lat_lon = false;

  let hours;
  if (store.Hours == null) {
    hours = NO_DATA;
  } else if (store.Hours2 == null) {
    hours = store.Hours.split('"').join();
  } else {
    hours = `${store.Hours}, ${store.Hours2}`
      .trim()
      .split('"')
      .join();
  }

  const store_ = new Store(
    locator_domain,
    locator_name,
    address,
    city,
    state,
    zip,
    country_code,
    store_number,
    phone,
    location_type,
    naics_code,
    latitude,
    longitude,
    external_lat_lon,
    hours
  );
  return store_;
}

async function run(outputToCSV, csvFile) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.setUserAgent(
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
  );

  page.on('response', async response => {
    if (response.url().endsWith('GetAllStores')) {
      const body = await response.json();
      const stores = new Stores(outputToCSV, csvFile);
      for (const store of body.d) {
        stores.addStore(makeStore(store));
      }
      await stores.write();
    }
  });

  await page.goto('https://www.shopnsavefood.com/locations');

  await browser.close();
}

(async () => {
  program.option('-o, --csv <csv>', 'Relative path to the CSV file to output data to');

  program.parse(process.argv);

  if (program.csv) {
    console.log(`Running crawl and outputting data to ${program.csv}`);
    await run(true, program.csv);
  } else {
    console.log(`Running crawl and outputting data to stdout`);
    await run(false);
  }
})();
