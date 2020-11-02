const Apify = require('apify');

const {
  locationObjectSelector,
} = require('./selectors');

const {
  formatObject,
  formatPhoneNumber,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.bakersplus.com/storelocator-sitemap.xml',
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
    },
    gotoFunction: async ({
      request, page,
    }) => {
      await page.goto(request.url, {
        timeout: 0, waitUntil: 'networkidle0',
      });
    },
    maxRequestsPerCrawl: 600,
    maxConcurrency: 10,
    handlePageFunction: async ({
      request, page,
    }) => {
      const isBlocked = await page.evaluate(() => {
        return document.body.innerText.startsWith('Access Denied')
      });
      if (isBlocked) {
        throw new Error("Page blocked");
      }
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/www.bakersplus.com\/stores\/details\//))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        await page.waitFor(5000);
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        if (await page.$(locationObjectSelector) !== null) {
          await page.waitForSelector(locationObjectSelector, { waitUntil: 'load', timeout: 0 });
          const locationObjectRaw = await page.$eval(locationObjectSelector, s => s.innerText);
          const locationObject = formatObject(locationObjectRaw);

          const poiData = {
            locator_domain: 'bakersplus.com',
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
            hours_of_operation: locationObject.openingHours[0],
          };
          const poi = new Poi(poiData);
          await Apify.pushData(poi);
        }
      }
    },
  });

  await crawler.run();
});
