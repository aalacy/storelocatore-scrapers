const Apify = require('apify');

const {
  locationObjectSelector1,
  locationObjectSelector2,
} = require('./selectors');

const {
  parseObject1,
  formatObject,
  formatAddressLine2,
  formatCountry,
  cleanState,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteUrl = 'https://www.fuelbodylab.com/contact';

  const requestList = new Apify.RequestList({
    sources: [{ url: siteUrl }],
  });
  await requestList.initialize();

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ page }) => {
      /* eslint-disable camelcase */
      const locationObjectsRaw1 = await page.$$eval(locationObjectSelector1, se => se
        .map(e => e.innerText));
      const locationObjectsRaw2 = await page.$$eval(locationObjectSelector2, se => se
        .map(e => e.getAttribute('data-block-json')));

      const locationObjects1 = locationObjectsRaw1.map(e => parseObject1(e));
      const locationObjects2 = locationObjectsRaw2.map(e => formatObject(e));

      /* eslint-disable no-restricted-syntax */
      for await (const [i, v] of locationObjects1.entries()) {
        /* eslint-disable camelcase */
        const { location_name, phone } = v;
        const object2 = locationObjects2[i].location;
        const street_address = object2.addressLine1;
        const addressLine2Raw = object2.addressLine2;
        const { city, state, zip } = formatAddressLine2(addressLine2Raw);
        const country_code = formatCountry(object2.addressCountry);
        const latitude = object2.mapLat;
        const longitude = object2.mapLng;

        const poiData = {
          locator_domain: 'fuelbodylab_com',
          location_name,
          street_address,
          city,
          state: cleanState(state),
          zip,
          country_code,
          phone,
          latitude,
          longitude,
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
