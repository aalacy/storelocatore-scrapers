const Apify = require('apify');
const {
  locationNameSelector,
  addressSelector,
  citySelector,
  stateSelector,
  zipCodeSelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hourSelector,
} = require('./selectors');

const {
  formatPhoneNumber,
  formatHours,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.libertytax.com/sitemaps/offices-3662/',
    userData: {
      urlType: 'initial',
    },
  });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    launchPuppeteerOptions: {
      headless: true,
      useChrome: true,
      stealth: true,
    },
    gotoFunction: async ({
      request, page,
    }) => {
      // Get current cookies from the page for certain URL
      const cookies = await page.cookies(request.url);
      // And remove them
      await page.deleteCookie(...cookies);
      await page.setViewport({
        width: 1920,
        height: 1080,
        deviceScaleFactor: 1,
      });
      await page.goto(request.url, {
        timeout: 0, waitUntil: 'networkidle0',
      });
    },
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 1,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/libertytax.com\/income-tax-preparation-locations\//))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        await page.waitFor(5000);
        console.log(locationUrls.length);
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        if (await page.$(addressSelector) !== null) {
          await page.waitForSelector(locationNameSelector, { waitUntil: 'load', timeout: 0 });
          /* eslint-disable camelcase */
          const location_name = await page.$eval(locationNameSelector, h => h.innerText);
          await page.waitFor(1000);
          const street_address = await page.$eval(addressSelector, e => e.innerText);
          const city = await page.$eval(citySelector, e => e.innerText);
          const state = await page.$eval(stateSelector, e => e.innerText);
          const zip = await page.$eval(zipCodeSelector, e => e.innerText);
          const phoneNumberRaw = await page.$eval(phoneSelector, p => p.innerText);
          const hoursRaw = await page.$eval(hourSelector, h => h.innerText);
          const phone = formatPhoneNumber(phoneNumberRaw);
          const latitude = await page.$eval(latitudeSelector, e => e.getAttribute('content'));
          const longitude = await page.$eval(longitudeSelector, e => e.getAttribute('content'));
          const hours_of_operation = formatHours(hoursRaw);

          const poiData = {
            locator_domain: 'libertytax.com',
            location_name,
            street_address,
            city,
            state,
            zip,
            phone,
            latitude,
            longitude,
            hours_of_operation,
          };
          const poi = new Poi(poiData);
          await Apify.pushData(poi);
        }
      }
    },
  });

  await crawler.run();
});
