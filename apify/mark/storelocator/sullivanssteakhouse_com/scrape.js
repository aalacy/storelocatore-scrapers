const Apify = require('apify');

const {
  addressSelector,
  hourSelector,
} = require('./selectors');

const {
  formatObject,
  decodeEntities,
  formatPhoneNumber,
  formatStreetAddress,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://sullivanssteakhouse.com/location-search/',
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
    maxRequestsPerCrawl: 50,
    maxConcurrency: 10,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await Apify.utils.enqueueLinks({
          page,
          requestQueue,
          selector: '#x-section-3 > div:nth-child(2) a',
          pseudoUrls: [
            'https://sullivanssteakhouse.com/[.*]/',
          ],
          userData: {
            urlType: 'detail',
          },
        });
        await page.waitFor(5000);
      }
      if (request.userData.urlType === 'detail') {
        await page.waitFor(3000);
        await page.waitForSelector(addressSelector, { waitUntil: 'load', timeout: 0 });
        // const address = await page.$eval(addressSelector, a => a.innerText);
        // const addressCompare = address.trim().substring(0, 8);
        await page.waitForSelector('script', { waitUntil: 'networkIdle0', timeout: 0 });
        const allLocationObjects = await page.$$eval('script', oe => oe.map(o => o.innerText));
        const locationObjectRaw = allLocationObjects.filter(e => e.includes('schema.org'));
        await page.waitForSelector(hourSelector);
        const hoursRaw = await page.$eval(hourSelector, h => h.innerText);
        /* eslint-disable camelcase */
        const hours_of_operation = formatHours(hoursRaw);

        if (locationObjectRaw[0] !== '') {
          const locationObjectRawItem = locationObjectRaw[0];
          const locationObjectRemoveEncoding = decodeEntities(locationObjectRawItem);
          const locationObject = formatObject(locationObjectRemoveEncoding);
          const street_address = formatStreetAddress(locationObject.address.streetAddress, locationObject.address.postalCode);

          const poiData = {
            locator_domain: 'sullivanssteakhouse.com',
            location_name: locationObject.name,
            street_address,
            city: locationObject.address.addressLocality,
            state: locationObject.address.addressRegion,
            zip: locationObject.address.postalCode,
            country_code: undefined,
            store_number: undefined,
            phone: formatPhoneNumber(locationObject.telephone),
            location_type: locationObject['@type'],
            naics_code: undefined,
            latitude: locationObject.geo.latitude,
            longitude: locationObject.geo.longitude,
            hours_of_operation,
          };
          const poi = new Poi(poiData);
          await Apify.pushData(poi);
          await page.waitFor(1000);
        }
      }
    },
  });

  await crawler.run();
});
