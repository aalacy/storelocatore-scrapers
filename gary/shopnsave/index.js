const puppeteer = require('puppeteer');
const program   = require('commander');

const Store   = require('./store.js').Store;
const Stores  = require('./store.js').Stores;
const NO_DATA = require('./store.js').NO_DATA;

function makeStore(store) {
  let locator_domain   = 'www.shopnsavefood.com';
  let locator_name     = store['Name'];
  let address          = store['Address1'];
  let city             = store['City'];
  let state            = store['State'];
  let zip              = store['Zip'];
  let country_code     = 'US';
  let store_number     = store['StoreID'];
  let phone            = store['Phone'];
  let location_type    = NO_DATA;
  let naics_code       = NO_DATA;
  let latitude         = store['Latitude'];
  let longitude        = store['Longitude'];
  let external_lat_lon = false;
 
  let hours;
  if (store['Hours'] == null) {
    hours = NO_DATA;
  } else if (store['Hours2'] == null) {
    hours = store['Hours'].split('"').join();
  } else {
    hours = `${store['Hours']}, ${store['Hours2']}`.trim().split('"').join();
  }
  
  const store_ = new Store(locator_domain,
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
                           hours);
  return store_;
}

async function run(outputToCSV, csvFile) {

  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36');

  page.on('response', async response => {
    if (response.url().endsWith('GetAllStores')) {
      let body = await response.json();
      let stores = new Stores(outputToCSV, csvFile);
      for(let store of body['d']) {
        stores.addStore(makeStore(store));
      }
      await stores.write();
    }
  });
  
  await page.goto('https://www.shopnsavefood.com/locations');
  
  await browser.close();
}

(async () => {
  program
    .option('-o, --csv <csv>', 'Relative path to the CSV file to output data to');
  
  program.parse(process.argv);

  if (program.csv) {
    console.log(`Running crawl and outputting data to ${program.csv}`);
    await run(true, program.csv);
  } else {
    console.log(`Running crawl and outputting data to stdout`);
    await run(false);
  }
}) ();
