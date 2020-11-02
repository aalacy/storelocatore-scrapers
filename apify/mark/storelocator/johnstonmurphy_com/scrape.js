const Apify = require('apify');

const {
  createStorageObject,
  getStoreID,
  storeKey,
  parseGoogleMapsUrl,
  pullFromPage,
} = require('./tools');

const {
  storeSelector,
  factorySelector,
  departmentSelector,
  detailStoreName,
  detailAddress,
  detailGeoLocation,
} = require('./selectors');

const {
  usLocationRequest,
  canadaLocationRequest,
} = require('./requests');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  // Opening a key value store until end before we format results
  const dataStorage = await Apify.openKeyValueStore('poidata');
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest(usLocationRequest);
  await requestQueue.addRequest(canadaLocationRequest);

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
    maxRequestsPerCrawl: 1000,
    maxConcurrency: 4,
    handlePageFunction: async ({ request, page }) => {
      // Storing data to be adjusted later after going into detail pages
      const stores = createStorageObject(request, page, dataStorage, storeSelector, 'Store');
      const factories = createStorageObject(request, page, dataStorage, factorySelector, 'Factory');
      const departments = createStorageObject(request, page, dataStorage, departmentSelector, 'Department/Specialty');

      // If its the initial request, then pull poi from the page
      if (request.userData.urlType === 'initial') {
        await pullFromPage(stores);
        await pullFromPage(factories);
        await pullFromPage(departments);

        // Some locations have inner detail pages, so go through these and find geolocation
        const enqueued = await Apify.utils.enqueueLinks({
          page,
          requestQueue,
          selector: 'a.store-detail-link',
          pseudoUrls: [
            'https://www.johnstonmurphy.com/on/demandware.store/Sites-johnston-murphy-us-Site/en_US/Stores-Details?StoreID=[.*]',
          ],
          userData: {
            urlType: 'detail',
          },
        });
        console.log(`Adding ${enqueued.length} to the queue.`);
      }
      if (request.userData.urlType === 'detail') {
        await page.waitFor(2000);
        const storeID = getStoreID(request.url);
        // Get the address + location name to create a key
        await page.waitForSelector(detailStoreName, { waitUntil: 'load', timeout: 0 });
        const storeName = await page.$eval(detailStoreName, h => h.innerText);

        await page.waitForSelector(detailAddress, { waitUntil: 'load', timeout: 0 });
        const address = await page.$eval(detailAddress, s => s.innerText);

        await page.waitForSelector(detailGeoLocation, { waitUntil: 'load', timeout: 0 });
        const geoUrl = await page.$eval(detailGeoLocation, a => a.href);
        const latLon = parseGoogleMapsUrl(geoUrl);

        // Once we have more info, store get our persisted info and add geo + storeID if it has one
        const searchKey = storeKey(storeName, address);
        const currentStoreData = await dataStorage.getValue(searchKey);
        if (currentStoreData) {
          const revisedStoreData = {
            ...currentStoreData,
            ...latLon,
            store_number: storeID,
          };
          // Upload new
          await dataStorage.setValue(searchKey, revisedStoreData);
        }
      }
      // After pulling store info from page, check for links and check links for store detail
      // We need to retrieve lat/long from these sources + store number
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
