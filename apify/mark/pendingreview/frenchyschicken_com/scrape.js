const Apify = require('apify');

const {
  locationLinkSelector,
  locationHrefSelector,
  locationNameSelector,
  locationInfoSelector,
  hoursSelector,
} = require('./selectors');

const {
  extractLocationInfo,
  parseGoogleUrl,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const baseUrl = 'http://www.frenchyschicken.com';
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'http://www.frenchyschicken.com/locations',
    userData: {
      urlType: 'initial',
    },
  });

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        const locations = await page.$(locationLinkSelector);
        const locationLinks = await locations.$$eval(locationHrefSelector, ae => ae.map(a => a.getAttribute('href')));
        const allRequests = locationLinks.map(e => ({ url: `${baseUrl}${e}`, userData: { urlType: 'detail' } }));
        /* eslint-disable no-restricted-syntax */
        for await (const url of allRequests) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        /* eslint-disable camelcase */
        const locator_domain = 'frenchyschicken.com';
        const location_name = await page.$eval(locationNameSelector, e => e.innerText);
        const locationInfoRaw = await page.$eval(locationInfoSelector, e => e.innerText);
        const locationInfo = extractLocationInfo(locationInfoRaw);
        let googleFrame;
        for (const frame of page.mainFrame().childFrames()) {
          if (frame.url().includes('google')) {
            googleFrame = frame;
          }
        }
        /* eslint-disable dot-notation */
        const geoUrl = googleFrame['_url'];
        const latLong = parseGoogleUrl(geoUrl);
        const hoursRaw = await page.$eval(hoursSelector, e => e.innerText);
        const poiData = {
          locator_domain,
          location_name,
          ...locationInfo,
          ...latLong,
          hours_of_operation: formatHours(hoursRaw),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
    maxRequestsPerCrawl: 20,
    maxConcurrency: 10,
    launchPuppeteerOptions: {
      headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy,
    },
    gotoFunction: async ({
      request, page,
    }) => {
      await page.goto(request.url, {
        timeout: 60000, waitUntil: 'networkidle0',
      });
    },
  });

  await crawler.run();
});
