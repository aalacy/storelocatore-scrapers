const puppeteer = require('puppeteer');
const ObjectsToCsv = require('objects-to-csv');
const mkdirp = require('mkdirp');
const Apify = require('apify');

(async () => {
  const url =
    'https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores';
  // Constants for file outputs
  const vendor_name = 'ShopNSave';
  const scrapped_domain = 'shopnsavefood.com';
  // date formatting -> use dateStr
  const date = new Date();
  const dateStr = `${date.getFullYear()}/${date.getMonth()}/${date.getDate()}/${new Date()
    .toUTCString()
    .split(' ')[4]
    .substring(0, 2)}${new Date()
    .toUTCString()
    .split(' ')[4]
    .substring(3, 5)}`;
  const dirpath = `./${scrapped_domain}/${dateStr}/`;

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1920, height: 1080 },
  });

  const page = await browser.newPage();
  await page.goto(url, { waituntil: 'load' });
  await page.waitFor(3000);
  const stores = await page.$$eval(
    '#collapsible0 > div.expanded > div.collapsible-content > div.collapsible > div.expanded > div.collapsible-content',
    elements => {
      const stores = [];
      for (const e of elements) {
        const fields = e.querySelectorAll('div > span:nth-child(2)');
        const store_obj = {
          locator_domain: 'https://www.shopnsavefood.com/',
          location_name: fields[2].innerText,
          street_address: fields[3].innerText,
          city: fields[4].innerText,
          state: fields[5].innerText,
          zip: fields[6].innerText,
          country_code: 'US',
          store_number: fields[0].innerText,
          phone: fields[1].innerText,
          location_type: {
            gas_station: fields[9].innerText,
            active: fields[10].innerText,
            pump_perk: fields[11].innerText,
          },
          niacs_code: null,
          latitude: fields[7].innerText,
          longitude: fields[8].innerText,
          external_lat_long: false,
          hours_of_operation: null,
        };
        stores.push(store_obj);
      }
      return stores;
    }
  );

  browser.close();
  const csv = new ObjectsToCsv(stores);

  // save to files
  // await mkdirp.sync(dirpath);
  // await csv.toDisk(dirpath+ 'stores.csv', { bom: false });
  // console.log("Created "+dirpath+'stores.csv');
  await Apify.pushData(stores);
})();
