const Apify = require('apify');

const {
  formatObject,
  formatPhoneNumber,
  parseGoogleMapsUrl,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.cspire.com/apache/stores.xml',
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
    maxRequestsPerCrawl: 200,
    maxConcurrency: 10,
    handlePageFunction: async ({
      request, page,
    }) => {
      const isBlocked = await page.evaluate(() => {
        return document.body.innerText.startsWith('Access Denied');
      });
      if (isBlocked) {
        throw new Error('Page blocked');
      }
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/www.cspire.com\/cms\/stores/))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        /* eslint-disable camelcase */
        const location_name = await page.$eval('div.header-field.store-name', e => e.innerText);
        await page.waitForSelector('script', { waitUntil: 'load', timeout: 0 });
        const allScripts = await page.$$eval('script', se => se.map(s => s.innerText));
        const locationScriptRaw = allScripts.filter(e => e.includes('GeoCoordinates'));
        const [locationObjectRaw] = locationScriptRaw;
        const locationObject = formatObject(locationObjectRaw);
        let { latitude, longitude } = locationObject.geo;

        if (latitude.length < 7 || longitude.length < 7) {
          await page.waitForSelector('#map > div > div > div:nth-child(3) > a', { waitUntil: 'networkidle0', timeout: 30000 });
          const geoUrl = await page.$eval('#map > div > div > div:nth-child(3) > a', e => e.getAttribute('href'));
          ({ latitude, longitude } = parseGoogleMapsUrl(geoUrl));
        }
        const poiData = {
          locator_domain: 'cspire_com',
          location_name,
          street_address: locationObject.address.streetAddress,
          city: locationObject.address.addressLocality,
          state: locationObject.address.addressRegion,
          zip: locationObject.address.postalCode,
          country_code: undefined,
          store_number: undefined,
          phone: formatPhoneNumber(locationObject.telephone),
          location_type: locationObject['@type'],
          latitude,
          longitude,
          hours_of_operation: locationObject.openingHours[0],
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();
});
