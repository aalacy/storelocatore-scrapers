const Apify = require('apify');

const {
  enqueueStatePages,
  enqueueCityPages,
  enqueueDetailPages,
} = require('./routes');

const {
  locationInfoExists,
  locationNameSelector,
  checkAddressSelector,
  streetSelector,
  streetAddress2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  hourSelector,
} = require('./selectors');

const {
  formatPhoneNumber,
  formatHours,
  formatData,
} = require('./tools');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://locations.haircuttery.com/index.html?utm_source=Yext&utm_medium=Pages&utm_campaign=Crumbs',
    userData: {
      urlType: 'initial',
    },
  });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ request, page }) => {
      // Site has inner layers that also have details links
      if (request.userData.urlType === 'initial') {
        await page.waitFor(5000);
        await enqueueStatePages({ page }, { requestQueue });
        await enqueueDetailPages({ page }, { requestQueue });
      }
      if (request.userData.urlType === 'state') {
        await page.waitFor(5000);
        await enqueueCityPages({ page }, { requestQueue });
        await enqueueDetailPages({ page }, { requestQueue });
      }
      if (request.userData.urlType === 'city') {
        await page.waitFor(5000);
        await enqueueDetailPages({ page }, { requestQueue });
      }
      if (request.userData.urlType === 'detail') {
        if (await page.$(locationInfoExists) !== null) {
          await page.waitForSelector(locationNameSelector, { waitUntil: 'load', timeout: 0 });
          /* eslint-disable camelcase */
          const location_name = await page.$eval(locationNameSelector, e => e.innerText);
          let street_address;
          const locationAddressElements = await page.$$eval(checkAddressSelector, h => h);
          // Some addresses have two lines for the address
          if (locationAddressElements.length === 2) {
            const street1 = await page.$eval(streetSelector, e => e.innerText);
            await page.waitForSelector(streetAddress2Selector);
            const street2 = await page.$eval(streetAddress2Selector, e => e.innerText);
            street_address = `${street1}, ${street2}`;
          }
          if (locationAddressElements.length === 1) {
            street_address = await page.$eval(streetSelector, e => e.innerText);
          }
          const city = await page.$eval(citySelector, e => e.innerText);
          const state = await page.$eval(stateSelector, e => e.innerText);
          const zip = await page.$eval(zipSelector, e => e.innerText);
          const phoneNumberRaw = await page.$eval(phoneSelector, p => p.innerText);
          const hoursRaw = await page.$eval(hourSelector, h => h.innerText);
          const phone = formatPhoneNumber(phoneNumberRaw);
          const hours_of_operation = formatHours(hoursRaw);

          const poi = {
            locator_domain: 'haircuttery.com',
            location_name,
            street_address,
            city,
            state,
            zip,
            phone,
            country_code: 'US',
            location_type: 'Salon',
            hours_of_operation,
          };
          await Apify.pushData(formatData(poi));
          await page.waitFor(5000);
        } else {
          await page.waitFor(5000);
          if (!requestQueue.isEmpty) {
            await requestQueue.fetchNextRequest();
          }
        }
      }
    },
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 3,
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
      timeout: 0, waitUntil: 'load',
    }),
  });

  await crawler.run();
});

module.exports = {
  Apify,
};
