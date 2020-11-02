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
    url: 'https://www.ralphs.com/storelocator-sitemap.xml',
    userData: {
      urlType: 'initial',
    },
  });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    launchPuppeteerOptions: {
      headless: true,
      useChrome: true,
			stealth: true,
			useApifyProxy: true,
    },
    handlePageFunction: async ({ request, page }) => {
      const isBlocked = await page.evaluate(() => document.body.innerText.startsWith('Access Denied'));
      if (isBlocked) {
        throw new Error('Page blocked');
      }
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/www.ralphs.com\/stores\/details\//))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        await page.waitForSelector('main', { timeout: 0 });
        const allScripts = await page.$$eval(locationObjectSelector, se => se
          .map(s => s.innerText));
        const locationObjectScript = allScripts.filter(e => e.includes('GeoCoordinates'));
        const locationObjectRaw = locationObjectScript[0];
        const locationObject = formatObject(locationObjectRaw);

        const poiData = {
          locator_domain: 'ralphs.com',
          location_name: locationObject.name,
          street_address: locationObject.address.streetAddress,
          city: locationObject.address.addressLocality,
          state: locationObject.address.addressRegion,
          zip: locationObject.address.postalCode,
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
    maxRequestsPerCrawl: 200,
    maxConcurrency: 10,
  });

  await crawler.run();
});
