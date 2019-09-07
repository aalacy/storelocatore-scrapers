const Apify = require('apify');

const {
  enqueueStatePages,
  enqueueCityPages,
  enqueueDetailPages,
} = require('./routes');

const {
  locationNameSelector,
  streetSelector,
  streetAddress2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  countrySelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hourSelector,
} = require('./selectors');

const {
  formatName,
  formatPhoneNumber,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

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
    launchPuppeteerOptions: {
      headless: true,
      useChrome: true,
      stealth: true,
    },
    gotoFunction: async ({
      request, page,
    }) => {
      await page.goto(request.url, {
        timeout: 30000, waitUntil: 'load',
      });
    },
    maxRequestsPerCrawl: 700,
    maxConcurrency: 5,
    maxRequestRetries: 2,
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
        /* eslint-disable camelcase */
        const locationNameRaw = await page.$eval(locationNameSelector, e => e.innerText);
        const location_name = formatName(locationNameRaw);
        let street_address = await page.$eval(streetSelector, e => e.innerText);
        if (await page.$(streetAddress2Selector) !== null) {
          const streetAddress2 = await page.$eval(streetAddress2Selector, e => e.innerText);
          street_address += `, ${streetAddress2}`;
        }
        const city = await page.$eval(citySelector, e => e.innerText);
        const state = await page.$eval(stateSelector, e => e.innerText);
        const zip = await page.$eval(zipSelector, e => e.innerText);
        const phoneNumberRaw = await page.$eval(phoneSelector, p => p.innerText);
        const country_code = await page.$eval(countrySelector, e => e.innerText);
        const phone = formatPhoneNumber(phoneNumberRaw);
        const latitude = await page.$eval(latitudeSelector, e => e.getAttribute('content'));
        const longitude = await page.$eval(longitudeSelector, e => e.getAttribute('content'));
        const hoursRaw = await page.$eval(hourSelector, h => h.innerText);
        const hours_of_operation = formatHours(hoursRaw);

        const poiData = {
          locator_domain: 'stores.sleepnumber.com',
          location_name,
          street_address,
          city,
          state,
          zip,
          country_code,
          phone,
          latitude,
          longitude,
          hours_of_operation,
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
        await page.waitFor(2000);
      }
    },
  });

  await crawler.run();
});

module.exports = {
  Apify,
};
