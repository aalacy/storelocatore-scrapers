const Apify = require('apify');

const {
  locationElementSelector,
  locationNameSelector,
  addressBlockSelector,
  phoneSelector,
  hourSelector,
} = require('./selectors');

const {
  formatLocationName,
  createGenericAddress,
  extractLocationInfo,
  storeKey,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  // Open a store to remove duplicates
  const dataStorage = await Apify.openKeyValueStore('poidata');
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ url: 'https://www.marinelayer.com/pages/stores' });

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ page }) => {
      const locationElement = await page.$$(locationElementSelector);
      /* eslint-disable no-restricted-syntax */
      for await (const v of locationElement) {
        /* eslint-disable camelcase */
        const location_name = await v.$eval(locationNameSelector, e => e.innerText);
        const addressBlockRaw = await v.$eval(addressBlockSelector, e => e.innerHTML);
        const addressString = createGenericAddress(addressBlockRaw);
        const addressBlock = extractLocationInfo(addressString);
        const phone = await v.$eval(phoneSelector, e => e.innerText);
        const hours_of_operation = await v.$eval(hourSelector, e => e.innerText);

        const poiData = {
          locator_domain: 'marinelayer.com',
          location_name: formatLocationName(location_name),
          ...addressBlock,
          phone,
          hours_of_operation,
        };
        const key = storeKey(poiData.street_address);
        await dataStorage.setValue(key, poiData);
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
  if (requestQueue.isFinished()) {
    await dataStorage.forEachKey(async (key) => {
      if (key) {
        const storeInfo = await dataStorage.getValue(key);
        const poi = new Poi(storeInfo);
        await Apify.pushData(poi);
      }
    });
  }
});
