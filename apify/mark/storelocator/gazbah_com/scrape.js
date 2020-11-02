const Apify = require('apify');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ url: 'https://www.gazbah.com/locations.cfm' });

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ page }) => {
      const locationRows = await page.$$('body > div.container > div.content > table > tbody > tr');
      /* eslint-disable no-restricted-syntax */
      for await (const [i, v] of locationRows.entries()) {
        // First row is the title of each column
        if (i !== 0) {
          /* eslint-disable camelcase */
          const store_number = await v.$eval('td:nth-child(1)', e => e.innerText);
          const location_type = await v.$eval('td:nth-child(2)', e => e.innerText);
          const street_address = await v.$eval('td:nth-child(3)', e => e.innerText);
          const city = await v.$eval('td:nth-child(4)', e => e.innerText);
          const state = await v.$eval('td:nth-child(5)', e => e.innerText);
          const phone = await v.$eval('td:nth-child(6)', e => e.innerText);
          const hourStart = await v.$eval('td:nth-child(8)', e => e.innerText);
          const hourEnd = await v.$eval('td:nth-child(9)', e => e.innerText);
          let hours_of_operation;
          if (hourEnd && hourEnd.length > 0) {
            hours_of_operation = `${hourStart} - ${hourEnd}`;
          } else {
            hours_of_operation = `${hourStart}`;
          }

          const poiData = {
            locator_domain: 'gazbah.com',
            street_address,
            city,
            state,
            store_number,
            phone,
            location_type,
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
      headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy,
    },
  });

  await crawler.run();
});
