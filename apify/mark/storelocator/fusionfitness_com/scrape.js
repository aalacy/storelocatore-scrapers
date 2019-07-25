const Apify = require('apify');

const {
  locationLinkSelector,
  locationHrefSelector,
  locationNameSelector,
  locationInfoSelector,
  phoneSelector,
} = require('./selectors');

const {
  extractLocationInfo,
  formatPhoneNumber,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const baseUrl = 'http://fusionfitness.com';
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'http://fusionfitness.com/',
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
        const locator_domain = 'fusionfitness.com';
        const locationNameRaw = await page.$eval(locationNameSelector, e => e.innerText);
        const location_name = locationNameRaw.substring(0, locationNameRaw.indexOf('|'));
        const locationInfoRaw = await page.$eval(locationInfoSelector, e => e.getAttribute('content'));
        const locationInfo = extractLocationInfo(locationInfoRaw);
        const infoBlock = await page.$eval(phoneSelector, e => e.innerText);
        const infoBlockNoSpace = infoBlock.replace(/\s/g, '');
        const phoneRaw1 = infoBlockNoSpace.match(/[0-9]{3}-[0-9]{3}-[0-9]{4}/);
        const phoneRaw2 = phoneRaw1[0];
        const phone = formatPhoneNumber(phoneRaw2);
        const poiData = {
          locator_domain,
          location_name,
          ...locationInfo,
          phone,
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
    maxRequestsPerCrawl: 20,
    maxConcurrency: 1,
    launchPuppeteerOptions: {
      headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy,
    },
  });

  await crawler.run();
});
