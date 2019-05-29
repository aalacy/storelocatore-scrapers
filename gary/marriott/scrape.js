const Apify = require('apify');
const puppeteer = require('puppeteer');

const Store   = require('./store.js').Store;
const Stores  = require('./store.js').Stores;
const NO_DATA = require('./store.js').NO_DATA;

async function parsePage({request, page}) {
  try {
    await page.waitFor('address', { timeout: 5000 });
    const texts = [];
    const values = {};

    let dataLayer = await page.evaluate(() => dataLayer);

    let locator_domain = 'www.marriott.com';
    let locator_name =
        dataLayer['prop_brand_name'] == undefined ?
        NO_DATA : dataLayer['prop_brand_name'];
    let store_number = NO_DATA;
    let location_type =
        dataLayer['prop_brand_name'] == undefined ?
        NO_DATA : dataLayer['prop_brand_name'];
    let naics_code = NO_DATA;
    let external_lat_lon = false;
    let hours_of_operation = NO_DATA; 
    
    let streetAddress = await page.evaluate(
      () => document.querySelector('[itemprop="streetAddress"]').innerText);
    let zip = await page.evaluate(
      () => document.querySelector('[itemprop="postalCode"]').innerText);
    let phone = await page.evaluate(
      () => document.querySelector('[itemprop="telephone"]').innerText);
    let latitude = await page.evaluate(
      () => document.querySelector('[itemprop="latitude"]').innerText);
    let longitude = await page.evaluate(
      () => document.querySelector('[itemprop="longitude"]').innerText);
    await page.waitFor('[itemprop="addressLocality"]', { timeout: 5000 });
    let city = await page.evaluate(
      () => document.querySelector('[itemprop="addressLocality"]').innerText);
    let state = await page.evaluate(
      () => document.querySelector('[itemprop="addressRegion"]').innerText)
    let country_code = await page.evaluate(
      () => document.querySelector('[itemprop="addressCountry"]').innerText);
    
    const store = new Store(locator_domain,
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
                            hours_of_operation);
    const dataset = await Apify.openDataset('stores');
    await dataset.pushData(store);
    console.log(store.toString());
  } catch (e) {
    console.log(e);
  }
}

async function getHotelLinks(browser, page_) {
  let buttonsSelector = 'a.js-view-rate-btn-link.analytics-click.l-float-right ';
  let url = 'https://www.marriott.com/search/filterSearch.mi?page='
  let i = 0;
  let retries = 5;
  let urls = [];
  let running = true;
  while (running) {
    i += 1;
    for (let j = 0; j < retries; j+=1) {
      try {
        await page_.goto(url + i);
         
        //await next.click();
      
        await page_.waitForSelector(buttonsSelector);
        let buttons = await page_.$$eval(buttonsSelector, buttons => {
          return buttons.map(button => button.href);
        });
        
        for (let button of buttons) {
          urls.push(button);
          console.log(button);
        }
  
        let next = await page_.$('a[title="Next"]');

        if (next == undefined) {
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
  let directory = 'https://www.marriott.com/hotel-search.mi';
  await page.goto(directory, {waitUntil: 'networkidle0', timeout: 0});
  let selector = 'div.l-region-body.l-display-none.l-accordion-section.js-accordion-section.t-border-top.t-border-color-standard-110 div.l-center-align a';
  let href = await page.$eval(selector, form => form.href );
  console.log(href);
  
  await page.close();
  const page_ = await browser.newPage();
  await page_.goto(href, {waitUntil: 'networkidle0'});

  return await getHotelLinks(browser, page_);
  
}

async function getCanadaHotelLinks(browser, page) {
  let directory = 'https://www.marriott.com/hotel-search.mi';
  await page.goto(directory, {waitUntil: 'networkidle0', timeout: 0});
  let accordionSelector = '.l-accordion.js-accordion.l-region-cont.t-cursor-pointer.js-region-toggle';
  let canadaHREF = 'https://www.marriott.com/search/submitSearch.mi?destinationAddress.region=canada&searchType=InCity&filterApplied=false';
  await page.close();
  
  const page_ = await browser.newPage();
  await page_.goto(canadaHREF, {waitUntil: 'networkidle0'});

  return await getHotelLinks(browser, page_);
}

async function navigateToHotelDirectory(browser, page, stores) {
  console.log('Getting hotel information');
  let canadaURLs = await getCanadaHotelLinks(browser, page);
  let usURLs     = await getUSHotelLinks(browser, await browser.newPage());
  console.log(canadaURLs.length);
  console.log(usURLs.length);
  console.log('URLS');
  return canadaURLs.concat(usURLs);   
}

async function run(csvFile) {
  try {
    const browser = await puppeteer.launch({
      headless: true,
      //args: ['--no-sandbox', 'disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36');
    
    let stores = new Stores(true, csvFile);

    const dataset = await Apify.openDataset('stores');

    let crawl = true;
    let count = (await dataset.getInfo()).itemCount; 
    if (count > 0) {
      crawl = false;
    }
    
    const requestQueue = await Apify.openRequestQueue();
    
    let urls = [];
    if (crawl || !(await requestQueue.isEmpty())) {
      if (await requestQueue.isEmpty()) {
        // 1. Get urls with hotel information
        urls = await navigateToHotelDirectory(browser, page, stores);
        let urls_ = [...new Set(urls)];
        // 2. Add all the urls to the queue for crawling
        let i = 0;
        for (let url_ of urls_) {
          i += 1;
          //if (i == 0) continue;
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
        maxRequestsPerCrawl: 10000 ,
        maxConcurrency: 10 
      });
      console.log('Running crawler');
      await crawler.run();
      console.log('Crawler complete');
    }

    console.log('Writing stores');
    await dataset.map(store => {
      let state = store.state;
      if (state.length == 0) {
        state = NO_DATA;
      }
      const store_ = new Store(store.locator_domain, store.locator_name, store.street_address, store.city, state, store.zip, store.country_code, store.store_number, store.phone, store.location_type, store.naics_code, store.latitude, store.longitude, store.external_lat_lon, store.hours_of_operation);
      stores.addStore(store_);
    });
    
    await stores.write();
    await browser.close();
  } catch (err) {
    console.error(err);
  }
}

(async () => {
  let csv = process.env.CSV ? process.env.CSV : 'marriott.csv';
  console.log(`Running crawl and outputting data to ${csv}`);
  Apify.main(async () => {
    await run(csv);
  });
}) ();
