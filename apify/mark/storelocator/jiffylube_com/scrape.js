const Apify = require('apify');
const {
  locationExistsSelector,
  locationNameSelector,
  locationNumberSelector,
  addressLine1Selector,
  addressLine2Selector,
  phoneSelector,
  bingMapsUrlSelector,
  hourSelector,
} = require('./selectors');

const {
  formatPhoneNumber,
  formatAddressLine2,
  getGeo,
  formatHours,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.jiffylube.com/sitemap.xml',
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
        timeout: 30000, waitUntil: 'networkidle0',
      });
    },
    maxRequestsPerCrawl: 2114,
    maxConcurrency: 10,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/jiffylube.com\/locations\/store\//))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        await page.waitFor(5000);
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        if (await page.$(locationExistsSelector) !== null) {
          /* eslint-disable camelcase */
          const location_name = await page.$eval(locationNameSelector, h => h.getAttribute('aria-label'));
          const store_number = await page.$eval(locationNumberSelector, e => e.innerText);
          const street_address = await page.$eval(addressLine1Selector, e => e.innerText);
          const addressLine2Raw = await page.$eval(addressLine2Selector, a => a.innerHTML);
          const phoneNumberRaw = await page.$eval(phoneSelector, p => p.innerText);
          const hoursRaw = await page.$eval(hourSelector, h => h.innerText);
          await page.waitForSelector(bingMapsUrlSelector, { waitFor: 'load', timeout: 0 });
          const bingMapUrl = await page.$eval(bingMapsUrlSelector, e => e.href);
          const latLong = getGeo(bingMapUrl);
          const cityStateZip = formatAddressLine2(addressLine2Raw);
          const phone = formatPhoneNumber(phoneNumberRaw);
          const hours_of_operation = formatHours(hoursRaw);

          const poiData = {
            locator_domain: 'jiffylube.com',
            location_name,
            street_address,
            ...cityStateZip,
            country_code: undefined,
            store_number,
            phone,
            location_type: 'Service Center',
            ...latLong,
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
