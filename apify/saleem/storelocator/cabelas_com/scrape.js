const Apify = require('apify');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});


async function scrape() {

  // Necessary to use puppeteer, because page does not load from regular request?
  // most data is in js variable on the page, but for store hours have to go to store
  // individual pages
  // Begin scraper
  const requestQueue = await Apify.openRequestQueue()

  const rootAddress = 'https://www.cabelas.com/stores/stores_home.jsp';
  const records = [];

  async function loadStores (stores) {
    storePageRequests = [];
    for (const store of stores) {
      record = {
        locator_domain: 'cabelas_com',
        location_name: store.name,
        street_address: store.address.address1 + store.address.address2,
        city: store.address.city,
        state: store.address.region,
        zip: store.address.postalcsode,
        country_code: '<MISSING>',
        store_number: store.key,
        phone: store.phone,
        location_type: store.brand,
        latitude: store.point.match(/.*(?=,)/)[0],
        longitude: store.point.match(/(?<=, ).*/)[0],
        hours_of_operation: '<MISSING>',
      }
      url = (new URL(store.pageurl, 'https://www.cabelas.com')).toString();

      requestQueue.addRequest({
        url,
        userData: {
          record,
          requestType: 2
        }
      })
    }
  }

  async function loadHours (hours, record) {
    record.hours_of_operation = hours.trim().replace(/[\n\t\s]+/g, ' ');
    records.push(record);
  }

  requestQueue.addRequest({
    url: rootAddress,
    userData: { 
      requestType: 1
    }
  })
  
	const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ request, page }) => {
      // load location page and get variable with store data in it
      if (request.userData.requestType === 1) {
        loadStores(await page.evaluate(() => {
          return locs;
        }));
      // load store page to get hours from html elements
      } else {
        let pageFunction;
        hostname = (new URL(request.loadedUrl)).hostname

        // three different page layouts for the store pages
        switch (hostname) {
          case 'www.cabelas.ca':
            pageFunction = () => {
              return document.querySelector('.media-content .col:first-child').textContent;
            }
            break;
          case 'stores.basspro.com':
            pageFunction = () => {
              return document.querySelector('.c-location-hours').textContent;
            }
            break;
          case 'www.cabelas.com':
            pageFunction = () => {
              return document.querySelector('.storeHours ul').textContent;
            }
            break;
          default:
            throw `Scraper does not know how to handle store page from hostname: ${hostname}`
        }
        loadHours(await page.evaluate(pageFunction), request.userData.record);
      }
    },
		maxRequestsPerCrawl: 1000,
		maxConcurrency: 10,
		launchPuppeteerOptions: {headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy}
  })
  
  await crawler.run();
	return records;

	// End scraper

}
