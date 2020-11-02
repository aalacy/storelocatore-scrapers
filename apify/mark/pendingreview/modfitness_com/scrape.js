const Apify = require('apify');

const { formatAddressLine2, parseGoogleMapsUrl } = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ url: 'https://modfitness.com/studios' });

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ page }) => {
      const locationRows = await page.$$('div.itemsCollectionContent > div.item');
      /* eslint-disable no-restricted-syntax */
      for await (const [i, v] of locationRows.entries()) {
        /* eslint-disable camelcase */
        const location_name = await v.$eval('div.itemContent > h2', e => e.innerText);
        if (!location_name.includes('CLOSED')) {
          const street_address = await v.$eval('div.itemContent > div > ul > li:nth-child(1) > strong > a', e => e.innerText);
          const addressLine2 = await v.$eval('div.itemContent > div > ul > li:nth-child(2)', e => e.innerText);
          const { city, state, zip } = formatAddressLine2(addressLine2);
          const phone = await v.$eval('div.itemContent > div > ul > li:nth-child(5)', e => e.innerText);
          const geoUrl = await v.$eval('div.itemContent > div > ul > li:nth-child(1) > strong > a', e => e.getAttribute('href'));
          const { latitude, longitude } = parseGoogleMapsUrl(geoUrl);
          const poiData = {
            locator_domain: 'modfitness_com',
            location_name,
            street_address,
            city,
            state,
            zip,
            phone,
            latitude,
            longitude,
          };
          const poi = new Poi(poiData);
          await Apify.pushData(poi);
        }
      }
    },
    maxRequestsPerCrawl: 100,
    maxConcurrency: 10,
    launchPuppeteerOptions: {
      headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy,
    },
  });

  await crawler.run();
});
