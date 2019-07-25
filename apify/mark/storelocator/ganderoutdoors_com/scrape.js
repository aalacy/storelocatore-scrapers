const Apify = require('apify');

const {
  locationHrefSelector,
  locationNameSelector,
  addressSelector,
  phoneSelector,
  hoursSelector,
} = require('./selectors');

const {
  extractLocationInfo,
  formatHours,
  formatPhoneNumber,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const initialUrl = 'https://www.ganderoutdoors.com/store-locator';
  const baseUrl = 'https://www.ganderoutdoors.com';
  const browser = await Apify.launchPuppeteer({ headless: true });
  const page = await browser.newPage();
  await page.goto(initialUrl, { waitUntil: 'networkidle0', timeout: 30000 });
  const locationLinks = await page.$$eval(locationHrefSelector, se => se.map(s => s.getAttribute('href')));
  const allRequests = locationLinks.map(e => ({ url: `${baseUrl}${e}` }));

  const requestList = new Apify.RequestList({
    sources: allRequests,
  });
  await requestList.initialize();
  await browser.close();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({
      request,
      $,
    }) => {
      /* eslint-disable camelcase */
      // There is one duplicate on the site which has different request URL but has identical info.
      // The store uses the duplicate as an RV sales front?
      if (request.url !== 'https://www.ganderoutdoors.com/store-details?StoreID=GO653') {
        const location_name = $(locationNameSelector).text();
        const addressInfo = $(addressSelector).text();
        const addressInfoHTML = $(addressSelector).html();
        const phoneRaw = $(phoneSelector).text();
        const hours = $(hoursSelector).text();
        const addressData = extractLocationInfo(addressInfo, addressInfoHTML);
        const poiData = {
          locator_domain: 'ganderoutdoors.com',
          location_name,
          ...addressData,
          phone: formatPhoneNumber(phoneRaw),
          hours_of_operation: formatHours(hours),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
    minConcurrency: 5,
    maxConcurrency: 20,
    maxRequestRetries: 1,
    handlePageTimeoutSecs: 60,
  });

  await crawler.run();
});
