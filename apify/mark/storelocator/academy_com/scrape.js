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
  countrySelector,
  phoneSelector,
  geoSelector,
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
    url: 'https://stores.academy.com/',
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
          if (locationAddressElements.length === 4) {
            const street1 = await page.$eval(streetSelector, e => e.innerText);
            await page.waitForSelector(streetAddress2Selector);
            const street2 = await page.$eval(streetAddress2Selector, e => e.innerText);
            street_address = `${street1}, ${street2}`;
          }
          if (locationAddressElements.length === 3) {
            street_address = await page.$eval(streetSelector, e => e.innerText);
          }
          const city = await page.$eval(citySelector, e => e.innerText);
          const state = await page.$eval(stateSelector, e => e.innerText);
          const zip = await page.$eval(zipSelector, e => e.innerText);
          const country_code = await page.$eval(countrySelector, e => e.dataset.country);

          const phoneNumberRaw = await page.$eval(phoneSelector, p => p.innerText);
          const phone = formatPhoneNumber(phoneNumberRaw);

          await page.waitForSelector(geoSelector, { waitUntil: 'load', timeout: 0 });
          const latitude = await page.$eval(geoSelector, e => e.dataset.lat);
          const longitude = await page.$eval(geoSelector, e => e.dataset.lon);

          let hours_of_operation;
          if (await page.$(hourSelector) !== null) {
            const hoursRaw = await page.$eval(hourSelector, h => h.innerText);
            hours_of_operation = formatHours(hoursRaw);
          }
          if (await page.$(hourSelector) === null) {
            street_address = 'Coming Soon';
          }

          const poiData = {
            locator_domain: 'academy.com',
            location_name,
            street_address,
            city,
            state,
            zip,
            phone,
            country_code,
            latitude,
            longitude,
            hours_of_operation,
          };
          const poi = new Poi(poiData);
          await Apify.pushData(poi);
        }
      }
    },
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 10,
    launchPuppeteerOptions: {
      headless: true,
    },
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
        timeout: 0, waitUntil: 'networkidle0',
      }),
  });

  await crawler.run();
});

module.exports = {
  Apify,
};
