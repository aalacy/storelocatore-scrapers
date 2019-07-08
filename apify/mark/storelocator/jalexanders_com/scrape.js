const Apify = require('apify');

const {
  formatPhoneNumber,
  formatAddress,
  formatHours,
  parseGoogleMapsUrl,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: 'https://jalexanders.com/locations/' }],
  });
  await requestList.initialize();

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ page }) => {
      const allLocationDetails = await page.$$('.location-details');
      /* eslint-disable no-restricted-syntax */
      for await (const locationDetails of allLocationDetails) {
        const addressRaw = await locationDetails.$eval('a', a => a.innerHTML);
        const phoneRaw = await locationDetails.$eval('p:nth-child(2)', p => p.innerText);
        const hoursRaw = await locationDetails.$eval('.hours > p', h => h.innerText);
        const googleMapsUrl = await locationDetails.$eval('a', a => a.getAttribute('href'));
        const addressBlock = formatAddress(addressRaw);
        const geo = parseGoogleMapsUrl(googleMapsUrl);
        const poiData = {
          locator_domain: 'jalexanders.com',
          location_name: undefined,
          ...addressBlock,
          country_code: undefined,
          store_number: undefined,
          phone: formatPhoneNumber(phoneRaw),
          location_type: undefined,
          naics_code: undefined,
          ...geo,
          hours_of_operation: formatHours(hoursRaw),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
    maxRequestsPerCrawl: 1,
    maxConcurrency: 1,
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
