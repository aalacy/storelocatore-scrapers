const Apify = require('apify');

const {
  locationNameSelector,
  addressSelector,
  phoneSelector,
  geoSelector,
  hourSelector,
} = require('./selectors');

const {
  formatPhoneNumber,
  formatAddress,
  formatHours,
  parseGoogleMapsUrl,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const locationUrl = 'https://www.cocosbakery.com/locations/';
  const requestList = new Apify.RequestList({
    sources: [{ url: locationUrl }],
  });
  await requestList.initialize();

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ page }) => {
      const contentColumns = await page.$$('.fusion-column-content');
      /* eslint-disable no-restricted-syntax */
      for await (const contentColumn of contentColumns) {
        /* eslint-disable camelcase */
        const location_name = await contentColumn.$eval(locationNameSelector, h => h.innerText);
        const addressString = await contentColumn.$eval(addressSelector, e => e.innerHTML);
        const phoneRaw = await contentColumn.$eval(phoneSelector, e => e.innerText);
        const googleMapsUrl = await contentColumn.$eval(geoSelector, e => e.getAttribute('href'));
        const hoursRaw = await contentColumn.$eval(hourSelector, e => e.innerText);
        const addressBlock = formatAddress(addressString);
        const latLong = parseGoogleMapsUrl(googleMapsUrl);

        const poiData = {
          locator_domain: 'cocosbakery.com',
          location_name,
          ...addressBlock,
          phone: formatPhoneNumber(phoneRaw),
          ...latLong,
          hours_of_operation: formatHours(hoursRaw),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
    launchPuppeteerOptions: {
      headless: true,
    },
    maxRequestsPerCrawl: 1,
    maxConcurrency: 1,
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
      timeout: 0, waitUntil: 'load',
    }),
  });

  await crawler.run();
});
