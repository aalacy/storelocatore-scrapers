const Apify = require('apify');

const { Poi } = require('./Poi');

const { formatObject } = require('./tools');

Apify.main(async () => {
  const siteUrl = 'https://viefit.com/contact-vie/';

  const requestList = new Apify.RequestList({
    sources: [{ url: siteUrl }],
  });
  await requestList.initialize();

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ page }) => {
      const allScripts = await page.$$eval('script', se => se.map(s => s.innerText));
      const [locationObjectsScript] = allScripts.filter(e => e.includes('GeoCoordinates'));
      const locationObjectsRaw = formatObject(locationObjectsScript);
      const locationObjectsArray = locationObjectsRaw['@graph'].filter(e => e['@type'] !== 'Organization');
      /* eslint-disable no-restricted-syntax */
      for await (const v of locationObjectsArray) {
        /* eslint-disable camelcase */

        const location_name = v.name;
        const location_type = v['@type'];
        const street_address = v.address.streetAddress;
        const city = v.address.addressLocality;
        const state = v.address.addressRegion;
        const zip = v.address.postalCode;
        const phone = v.address.telephone;
        const { latitude, longitude } = v.geo;
        const [hours_of_operation] = v.openingHours;

        const poiData = {
          locator_domain: 'viefit_com',
          location_name,
          location_type,
          street_address,
          city,
          state,
          zip,
          phone,
          latitude,
          longitude,
          hours_of_operation,
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
    maxRequestsPerCrawl: 1,
    maxConcurrency: 10,
    launchPuppeteerOptions: {
      headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy,
    },
  });

  await crawler.run();
});
