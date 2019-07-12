const Apify = require('apify');

const {
  locationObjectSelector,
} = require('./selectors');

const {
  formatObject,
  formatPhoneNumber,
  formatHours,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.metromarket.net/storelocator-sitemap.xml',
    userData: {
      urlType: 'initial',
    },
  });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    launchPuppeteerOptions: {
      headless: true,
      useChrome: true,
      stealth: true
    },
    handlePageFunction: async ({ request, page }) => {
      const isBlocked = await page.evaluate(() => {
        return document.body.innerText.startsWith('Access Denied')
      });
      if (isBlocked) {
        throw new Error("Page blocked");
      }
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/www.metromarket.net\/stores\/details\//))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        /* eslint-disable no-restricted-syntax */
        for (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        await page.waitForSelector('main', { timeout: 0 });
        const locationObjectRaw = await page.$eval(locationObjectSelector, s => s.innerText);
        const locationObject = formatObject(locationObjectRaw);

        const poiData = {
          locator_domain: 'metromarket.net',
          location_name: locationObject.name,
          street_address: locationObject.address.streetAddress,
          city: locationObject.address.addressLocality,
          state: locationObject.address.addressRegion,
          zip: locationObject.address.postalCode,
          country_code: undefined,
          store_number: undefined,
          phone: formatPhoneNumber(locationObject.telephone),
          location_type: locationObject['@type'],
          latitude: locationObject.geo.latitude,
          longitude: locationObject.geo.longitude,
          hours_of_operation: formatHours(locationObject.openingHours),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
    maxRequestsPerCrawl: 100,
    maxConcurrency: 4,
  });

  await crawler.run();
});
