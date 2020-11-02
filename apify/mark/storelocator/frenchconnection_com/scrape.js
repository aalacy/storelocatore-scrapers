const Apify = require('apify');

const {
  countrySelector,
  allDataSelector,
} = require('./selectors');

const {
  extractLocationInfo,
  formatCountry,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ url: 'https://usa.frenchconnection.com/content/stores/united-states.htm' });

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ page }) => {
      const articleElement = await page.$(allDataSelector);
      const locationDataRaw = await articleElement.$$eval('p', pe => pe.map(p => p.innerText));
      const country = await page.$eval(countrySelector, e => e.innerText);
      /* eslint-disable no-restricted-syntax */
      for await (const [i] of locationDataRaw.entries()) {
        /* eslint-disable camelcase */
        const locationData = extractLocationInfo(locationDataRaw[i]);
        const poiData = {
          locator_domain: 'frenchconnection.com',
          ...locationData,
          country_code: formatCountry(country),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
    maxRequestsPerCrawl: 2,
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
