const Apify = require('apify');
const {
  locationNameSelector,
  storeDetailExistSelector,
  addressLine1Selector,
  addressLine2Selector,
  phoneSelector,
  hourSelector,
} = require('./selectors');

const {
  formatPhoneNumber,
  formatAddressLine1,
  formatAddressLine2,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.mybobs.com/stores',
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
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await Apify.utils.enqueueLinks({
          page,
          requestQueue,
          selector: 'a',
          pseudoUrls: [
            'https://www.mybobs.com/stores/[.*]/[.*]',
          ],
          userData: {
            urlType: 'detail',
          },
        });
        await page.waitFor(5000);
      }
      if (request.userData.urlType === 'detail') {
        if (await page.$(storeDetailExistSelector) !== null) {
          /* eslint-disable camelcase */
          const location_name = await page.$eval(locationNameSelector, l => l.innerText);
          const addressLine1 = await page.$eval(addressLine1Selector, a => a.innerText);
          const addressLine2 = await page.$eval(addressLine2Selector, a => a.innerText);
          const phoneNumber = await page.$eval(phoneSelector, p => p.innerText);
          const hoursRaw = await page.$eval(hourSelector, h => h.innerText);

          /* eslint-disable camelcase */
          const poiData = {
            locator_domain: 'mybobs.com',
            location_name,
            street_address: formatAddressLine1(addressLine1),
            ...formatAddressLine2(addressLine2),
            country_code: undefined,
            phone: formatPhoneNumber(phoneNumber),
            hours_of_operation: formatHours(hoursRaw),
          };
          const poi = new Poi(poiData);
          await Apify.pushData(poi);
          await page.waitFor(5000);
        }
      }
    },
  });

  await crawler.run();
});
