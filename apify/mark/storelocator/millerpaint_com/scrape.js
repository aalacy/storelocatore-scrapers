const Apify = require('apify');

const {
  millerPaintDealersCheckbox,
  millerPaintStoresCheckbox,
  locationElementSelector,
  locationNameSelector,
  addressBlockSelector,
  phoneSelector,
  hourSelector,
} = require('./selectors');

const {
  extractLocationInfo,
  storeKey,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  // Open a store to remove duplicates
  const dataStorage = await Apify.openKeyValueStore('poidata');
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ url: 'https://millerpaint.com/locations.html' });

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ page }) => {
      await page.waitForSelector(millerPaintStoresCheckbox);
      await page.click(millerPaintStoresCheckbox);
      await page.waitFor(1000);
      await page.$$(locationElementSelector, { waitUntil: 'networkidle0', timeout: 5000 });
      const locationElementDealer = await page.$$(locationElementSelector);
      /* eslint-disable no-restricted-syntax */
      for await (const v of locationElementDealer) {
        /* eslint-disable camelcase */
        const location_name = await v.$eval(locationNameSelector, e => e.innerText);
        const addressStringRaw = await v.$eval(addressBlockSelector, e => e.innerHTML);
        const addressBlock = extractLocationInfo(addressStringRaw);
        let phone;
        let hours_of_operation;
        if (await v.$(phoneSelector) !== null) {
          phone = await v.$eval(phoneSelector, e => e.innerText);
        }
        if (await v.$(hourSelector) !== null) {
          hours_of_operation = await v.$eval(hourSelector, e => e.innerText);
        }
        const poiData = {
          locator_domain: 'millerpaint.com',
          location_name,
          location_type: 'Dealer',
          ...addressBlock,
          phone,
          hours_of_operation,
        };
        const key = storeKey(poiData.street_address);
        await dataStorage.setValue(key, poiData);
      }
      await page.click(millerPaintStoresCheckbox);
      await page.click(millerPaintDealersCheckbox);
      await page.waitFor(1000);
      await page.$$(locationElementSelector, { waitUntil: 'networkidle0', timeout: 5000 });
      const locationElementStore = await page.$$(locationElementSelector);
      /* eslint-disable no-restricted-syntax */
      for await (const v of locationElementStore) {
        /* eslint-disable camelcase */
        const location_name = await v.$eval(locationNameSelector, e => e.innerText);
        const addressStringRaw = await v.$eval(addressBlockSelector, e => e.innerHTML);
        const addressBlock = extractLocationInfo(addressStringRaw);
        let phone;
        let hours_of_operation;
        if (await v.$(phoneSelector) !== null) {
          phone = await v.$eval(phoneSelector, e => e.innerText);
        }
        if (await v.$(hourSelector) !== null) {
          hours_of_operation = await v.$eval(hourSelector, e => e.innerText);
        }
        const poiData = {
          locator_domain: 'millerpaint.com',
          location_name,
          location_type: 'Store',
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
