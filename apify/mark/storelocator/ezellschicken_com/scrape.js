const Apify = require('apify');

const {
  locationInfoRawSelector,
} = require('./selectors');

const {
  formatLocationObject,
  parseGoogleUrl,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.ezellschicken.com/page/locations',
    userData: {
      urlType: 'initial',
    },
  });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector(locationInfoRawSelector);
        const allStoreInfos = await page.$$eval(locationInfoRawSelector, se => se
          .map(s => s.innerText));
        const allUrls = await page.$$eval('a', ae => ae.map(a => a.href));
        const googleMapUrls = allUrls.filter(e => e.includes('https://goo') || e.includes('https://www.google.com/maps'))
          .map((e) => {
            if (e.includes('https://www.google.com/maps/place/Ezell')) {
              return e;
            }
            return undefined;
          });

        /* eslint-disable no-restricted-syntax */
        for await (const [i, locationInfo] of allStoreInfos.entries()) {
          const poiNoGeo = formatLocationObject(locationInfo);
          const poiWithGeo = parseGoogleUrl(googleMapUrls[i]);
          const poiData = {
            locator_domain: 'ezellschicken.com',
            country_code: undefined,
            location_type: undefined,
            ...poiNoGeo,
            ...poiWithGeo,
          };
          const poi = new Poi(poiData);
          await Apify.pushData(poi);
        }
        await page.waitFor(1000);
      }
    },
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 4,
    launchPuppeteerOptions: {
      headless: true,
    },
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
      timeout: 0, waitUntil: 'load',
    }),
  });

  await crawler.run();
});
