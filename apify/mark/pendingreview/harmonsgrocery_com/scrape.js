const Apify = require('apify');

const {
  locationInfoSelector,
  locationNameSelector,
  addressBlockSelector,
  phoneSelector,
  hourSelector,
} = require('./selectors');

const {
  createGenericAddress,
  extractLocationInfo,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ url: 'https://www.harmonsgrocery.com/locations#/!store-locations' });

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ page }) => {
      const locationElement = await page.$$(locationInfoSelector);
      /* eslint-disable no-restricted-syntax */
      for await (const v of locationElement) {
        if (await v.$(hourSelector) !== null) {
          /* eslint-disable camelcase */
          const location_name = await v.$eval(locationNameSelector, e => e.innerText);
          const addressBlockRaw = await v.$eval(addressBlockSelector, e => e.innerHTML);
          const addressString = createGenericAddress(addressBlockRaw);
          const addressBlock = extractLocationInfo(addressString);
          const phone = await v.$eval(phoneSelector, e => e.innerText);
          const hours_of_operation = await v.$eval(hourSelector, e => e.innerText);
          const poiData = {
            locator_domain: 'harmonsgrocery.com',
            location_name,
            ...addressBlock,
            phone,
            latitude: '<INACCESSIBLE>',
            longitude: '<INACCESSIBLE>',
            hours_of_operation,
          };
          const poi = new Poi(poiData);
          await Apify.pushData(poi);
        }
      }
    },
    maxRequestsPerCrawl: 1,
    maxConcurrency: 1,
    launchPuppeteerOptions: {
      headless: true,
      stealth: true,
      useChrome: true,
      useApifyProxy: !!useProxy,
    },
  });

  await crawler.run();
});


/*


const poi = {
        locator_domain: 'safegraph.com',
        location_name: heading,
        street_address: '1543 mission st',
        city: 'san francisco',
        state: 'CA',
        zip: '94107',
        country_code: 'US',
        store_number: '<MISSING>',
        phone: '<MISSING>',
        location_type: '<MISSING>',
        latitude: 37.773500,
        longitude: -122.417774,
        hours_of_operation: '<MISSING>',
      };

*/
