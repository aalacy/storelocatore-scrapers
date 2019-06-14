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
  citySelector,
  stateSelector,
  zipSelector,
  streetAddress2Selector,
  cityAddress2Selector,
  stateAddress2Selector,
  zipAddress2Selector,
  phoneSelector,
  googleMapsUrlSelector,
  hourSelector,
} = require('./selectors');

const {
  formatPhoneNumber,
  formatHours,
  parseGoogleMapsUrl,
  formatData,
} = require('./tools');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://stores.sleepnumber.com/',
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
          let city;
          let state;
          let zip;
          const locationAddressElements = await page.$$eval(checkAddressSelector, h => h);
          // Some addresses have two lines for the address
          if (locationAddressElements.length === 4) {
            const street1 = await page.$eval(streetSelector, e => e.innerText);
            const street2 = await page.$eval(streetAddress2Selector, e => e.innerText);
            street_address = `${street1}, ${street2}`;
            city = await page.$eval(cityAddress2Selector, e => e.innerText);
            state = await page.$eval(stateAddress2Selector, e => e.innerText);
            zip = await page.$eval(zipAddress2Selector, e => e.innerText);
          }
          if (locationAddressElements.length === 3) {
            street_address = await page.$eval(streetSelector, e => e.innerText);
            city = await page.$eval(citySelector, e => e.innerText);
            state = await page.$eval(stateSelector, e => e.innerText);
            zip = await page.$eval(zipSelector, e => e.innerText);
          }
          const phoneNumberRaw = await page.$eval(phoneSelector, p => p.innerText);
          const hoursRaw = await page.$eval(hourSelector, h => h.innerText);
          const phone = formatPhoneNumber(phoneNumberRaw);
          await page.waitForSelector(googleMapsUrlSelector, { waitUntil: 'load', timeout: 0 });
          const googleMapsUrl = await page.$eval(googleMapsUrlSelector, e => e.href);
          const latLong = parseGoogleMapsUrl(googleMapsUrl);
          const hours_of_operation = formatHours(hoursRaw);

          const poi = {
            locator_domain: 'stores.sleepnumber.com',
            location_name,
            street_address,
            city,
            state,
            zip,
            phone,
            country_code: 'US',
            location_type: 'Store',
            ...latLong,
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
