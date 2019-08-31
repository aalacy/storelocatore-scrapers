const Apify = require('apify');
const {
  locationNameSelector,
  addressSelector,
  phoneSelector,
  hourSelector,
} = require('./selectors');

const {
  formatPhoneNumber,
  formatAddress,
  formatHours,
  removeEmptyStringProperties,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();

  await requestQueue.addRequest({
    url: 'https://www.homegoods.com/sitemap.xml',
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
      await page.goto(request.url, {
        timeout: 0, waitUntil: 'networkidle0',
      });
    },
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 10,
    maxRequestRetries: 1,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/homegoods.com\/store-details\//))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        await page.waitFor(5000);
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        await page.waitForSelector(locationNameSelector, { waitUntil: 'load', timeout: 0 });
        /* eslint-disable camelcase */
        const location_name = await page.$eval(locationNameSelector, h => h.innerText);
        const addressRaw = await page.$eval(addressSelector, a => a.innerHTML);
        const phoneNumberRaw = await page.$eval(phoneSelector, p => p.innerText);
        const hoursRaw = await page.$eval(hourSelector, h => h.innerHTML);
        const address = formatAddress(addressRaw);
        const phone = formatPhoneNumber(phoneNumberRaw);
        const hours_of_operation = formatHours(hoursRaw);

        const poiData = {
          locator_domain: 'homegoods.com',
          location_name,
          ...address,
          phone,
          hours_of_operation,
        };
        const cleanPoiData = removeEmptyStringProperties(poiData);
        const poi = new Poi(cleanPoiData);
        await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();
});
