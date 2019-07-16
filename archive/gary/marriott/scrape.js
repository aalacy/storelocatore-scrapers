const Apify = require('apify');
const puppeteer = require('puppeteer');

const { Store } = require('./store.js');
const { Stores } = require('./store.js');
const { NO_DATA } = require('./store.js');

async function parsePage({ request, page }) {
  // await page.waitForNavigation(15000, { waitUntil: 'networkidle2' });
  await page.waitFor('address', { timeout: 5000 });

  const texts = [];
  const values = {};

  const dataLayer = await page.evaluate(() => dataLayer);

  const locator_domain = 'www.marriott.com';
  const store_number = request.url
    .split('propertyCode')[1]
    .split('=')[1]
    .split('&')[0];
  const location_type =
    dataLayer.prop_brand_name === undefined ? NO_DATA : dataLayer.prop_brand_name;
  const naics_code = NO_DATA;
  const external_lat_lon = false;
  const hours_of_operation = NO_DATA;

  const locator_name = await page.evaluate(
    () => document.querySelector('[itemprop="name"]').innerText
  );
  const streetAddress = await page.evaluate(
    () => document.querySelector('[itemprop="streetAddress"]').innerText
  );
  const zip = await page.evaluate(
    () => document.querySelector('[itemprop="postalCode"]').innerText
  );
  const phone = await page.evaluate(
    () => document.querySelector('[itemprop="telephone"]').innerText
  );
  const latitude = await page.evaluate(
    () => document.querySelector('[itemprop="latitude"]').innerText
  );
  const longitude = await page.evaluate(
    () => document.querySelector('[itemprop="longitude"]').innerText
  );
  await page.waitFor('[itemprop="addressLocality"]', { timeout: 5000 });
  const city = await page.evaluate(
    () => document.querySelector('[itemprop="addressLocality"]').innerText
  );
  const state = await page.evaluate(
    () => document.querySelector('[itemprop="addressRegion"]').innerText
  );
  const country_code = await page.evaluate(
    () => document.querySelector('[itemprop="addressCountry"]').innerText
  );

  const store = new Store(
    locator_domain,
    locator_name,
    streetAddress,
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
    hours_of_operation
  );
  const dataset = await Apify.openDataset('stores');
  await dataset.pushData(store);
  console.log(request.url);
  console.log(store.toString());

  await page.close();
}

async function getHotelLinks(browser, page_) {
  const buttonsSelector = 'a.js-view-rate-btn-link.analytics-click.l-float-right ';
  const url = 'https://www.marriott.com/search/filterSearch.mi?page=';
  let i = 0;
  const retries = 5;
  const urls = [];
  let running = true;
  while (running) {
    i += 1;
    for (let j = 0; j < retries; j += 1) {
      try {
        await page_.goto(url + i);

        await page_.waitForSelector(buttonsSelector);
        const buttons = await page_.$$eval(buttonsSelector, buttons => {
          return buttons.map(button => button.href);
        });

        for (const button of buttons) {
          urls.push(button);
          console.log(button);
        }

        const next = await page_.$('a[title="Next"]');

        if (next === undefined) {
          running = false;
          break;
        }

        if (buttons.length > 0) {
          break;
        }
      } catch (e) {
        console.log(e);
        page_.reload();
      }
    }
  }
  return urls;
}

async function getUSHotelLinks(browser, page) {
  const directory = 'https://www.marriott.com/hotel-search.mi';
  await page.goto(directory, { waitUntil: 'networkidle0', timeout: 0 });
  const selector =
    'div.l-region-body.l-display-none.l-accordion-section.js-accordion-section.t-border-top.t-border-color-standard-110 div.l-center-align a';
  const href = await page.$eval(selector, form => form.href);
  console.log(href);

  await page.close();
  const page_ = await browser.newPage();
  await page_.goto(href, { waitUntil: 'networkidle0' });

  return getHotelLinks(browser, page_);
}

async function getCanadaHotelLinks(browser, page) {
  const directory = 'https://www.marriott.com/hotel-search.mi';
  await page.goto(directory, { waitUntil: 'networkidle0', timeout: 0 });
  const accordionSelector =
    '.l-accordion.js-accordion.l-region-cont.t-cursor-pointer.js-region-toggle';
  const canadaHREF =
    'https://www.marriott.com/search/submitSearch.mi?destinationAddress.region=canada&searchType=InCity&filterApplied=false';
  await page.close();

  const page_ = await browser.newPage();
  await page_.goto(canadaHREF, { waitUntil: 'networkidle0' });

  return getHotelLinks(browser, page_);
}

async function navigateToHotelDirectory(browser, page, stores) {
  console.log('Getting hotel information');
  const canadaURLs = await getCanadaHotelLinks(browser, page);
  const usURLs = await getUSHotelLinks(browser, await browser.newPage());
  console.log(canadaURLs.length);
  console.log(usURLs.length);
  console.log('URLS');
  return canadaURLs.concat(usURLs);
}

async function run(csvFile) {
  try {
    const browser = await puppeteer.launch({
      // headless: true,
    });
    const page = await browser.newPage();

    const stores = new Stores(true, csvFile);

    const dataset = await Apify.openDataset('stores');

    let crawl = true;
    const count = (await dataset.getInfo()).itemCount;
    if (count > 0) {
      crawl = false;
    }

    const requestQueue = await Apify.openRequestQueue();

    let urls = [];
    if (crawl || !(await requestQueue.isEmpty())) {
      if (await requestQueue.isEmpty()) {
        // 1. Get urls with hotel information
        urls = await navigateToHotelDirectory(browser, page, stores);
        const urls_ = [...new Set(urls)];
        // 2. Add all the urls to the queue for crawling
        let i = 0;
        for (const url_ of urls_) {
          i += 1;
          // if (i === 0) continue;
          try {
            await requestQueue.addRequest({ url: url_ });
          } catch (e) {
            console.log(e);
          }
        }
      }

      // 3. Crawl concurrently
      const crawler = new Apify.PuppeteerCrawler({
        requestQueue,
        handlePageFunction: parsePage,
        maxRequestsPerCrawl: 10000,
        maxConcurrency: 1,
        maxOpenPagesPerInstance: 1,
        puppeteerPoolOptions: {
          maxOpenPagesPerInstance: 1,
        },
        launchPuppeteerOptions: {
          useChrome: true,
          // stealth: true
        },
      });
      console.log('Running crawler');
      await crawler.run();
      console.log('Crawler complete');
    }

    console.log('Writing stores');
    const stores__ = [];

    /**
     * The callback to a map function needs a return value, as the purpose of
     * the map function is to map from one array of values to another array of
     * values. E.g. [a,a,a].map(a => a+1) === [a+1, a+1, a+1]
     */

    // eslint-disable-next-line array-callback-return
    await dataset.map(store => {
      let { state } = store;
      if (state.length === 0) {
        state = NO_DATA;
      }
      const store_ = new Store(
        store.locator_domain,
        store.locator_name,
        store.street_address,
        store.city,
        state,
        store.zip,
        store.country_code,
        store.store_number,
        store.phone,
        store.location_type,
        store.naics_code,
        store.latitude,
        store.longitude,
        store.external_lat_lon,
        store.hours_of_operation
      );
      stores.addStore(store_);
      stores__.push({
        locator_domain: store.locator_domain,
        location_name: store.location_name,
        street_address: store.street_address,
        city: store.city,
        state: store.state,
        zip: store.zip,
        country_code: store.country_code,
        store_number: store.store_number,
        phone: store.phone,
        location_type: store.location_type,
        naics_code: store.naics_code,
        latitude: store.latitude,
        longitude: store.longitude,
        hours_of_operation: store.hours_of_operation,
        external_lat_lon: store.external_lat_lon,
      });
    });

    await Apify.pushData(stores__);

    await stores.write();
    await browser.close();
  } catch (err) {
    console.error(err);
  }
}

(async () => {
  const csv = process.env.CSV ? process.env.CSV : 'marriott.csv';
  console.log(`Running crawl and outputting data to ${csv}`);
  Apify.main(async () => {
    await run(csv);
  });
})();
