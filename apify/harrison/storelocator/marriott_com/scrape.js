const puppeteer = require('puppeteer');
const ObjectsToCsv = require('objects-to-csv');
const mkdirp = require('mkdirp');
const Apify = require('apify');

const all_hotels = [];

// gets the hotels that are listed on a single page -> returns hotels on the page
async function get_page_hotels(page) {
  const hotels = await page.evaluate(() => {
    return Array.from(
      document.querySelectorAll(
        '#merch-property-results > div > div > div' +
          '> div > div:nth-child(2) > div:nth-child(2) > div'
      ),
      hotel => {
        // let name = hotel.querySelector("div > div > a.js-hotel-quickview-link > h2 > span");
        const details = hotel.querySelector('div:nth-child(2) > div');
        // console.log("D: " + details)
        return {
          locator_domain: 'https://www.marriott.com',
          location_name: null, // name.innerText,
          street_address: hotel.getAttribute('data-address-line1'),
          city: null, // details.innerText, //getAttribute('data-city'),
          state: hotel.getAttribute('data-state'),
          zip: hotel.getAttribute('data-postal-code'),
          country_code: hotel.getAttribute('data-country'),
          store_number: null,
          phone: hotel.getAttribute('data-contact'),
          location_type: null,
          niacs_code: null,
          latitude: null,
          longitude: null,
          external_lat_long: true,
          hours_of_operation: null,
        };
      }
    );
  });

  const names = await page.evaluate(() => {
    return Array.from(
      document.querySelectorAll(
        '#merch-property-results > div > div > div' +
          '> div > div:nth-child(2) > div > div > a.js-hotel-quickview-link > h2 > span'
      ),
      name => {
        return name.innerText;
      }
    );
  });

  for (let i = 0; i < names.length; i++) {
    hotels[i].location_name = names[i];
    await all_hotels.push(hotels[i]);
  }

  return Promise.all(hotels);
}

async function get_destination_info(browser, href) {
  const page = await browser.newPage();
  const hotels = [];
  await page
    .goto(`https://www.marriott.com${href}`, { waitUntil: 'networkidle0', timeout: 120000 })
    .catch(err => console.log(err));
  while ((await page.$('[title="Next"]')) != null) {
    hotels.push(...(await get_page_hotels(page)));
    await Promise.all([page.waitForNavigation(), page.click('[title="Next"]')]);
  }
  hotels.push(...(await get_page_hotels(page)));
  console.log(`Found : ${hotels.length}`);
  await page.close();
  return hotels;
}

async function get_state_hrefs(browser, url) {
  const page = await browser.newPage();
  console.log('Scrapping for states hrefs...');
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 0 });
  const hrefs = [];

  const toggles = await page.$$('.js-region-toggle');
  for (const toggle of toggles) {
    await toggle.click();
    const links = await toggle.$$eval('.m-state-list a', as => as.map(a => a.getAttribute('href')));
    hrefs.push(...links);
  }
  await page.close();
  return hrefs;
}

(async () => {
  // let url = 'https://www.marriott.com';
  // Constants for file outputs
  // const vendor_name = 'Marriott';
  const scrapped_domain = 'marriott.com';
  // date formatting -> use dateStr
  const date = new Date();
  const dateStr = `
    ${date.getFullYear()}/${date.getMonth()}/${date.getDate()}/${new Date()
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
  const hrefs = await get_state_hrefs(browser, 'https://www.marriott.com/hotel-search.mi');

  for (const href of hrefs) {
    await get_destination_info(browser, href);
  }

  browser.close();
  // let csv = new ObjectsToCsv(all_hotels);

  // save to files
  // await mkdirp.sync(dirpath);
  // await csv.toDisk(dirpath+ 'hotels.csv', { bom: false });
  // console.log("Created "+dirpath+'hotels.csv');

  // console.log("Created ./apify_storage/hotels.json");
  Apify.pushData(all_hotels);
})();
