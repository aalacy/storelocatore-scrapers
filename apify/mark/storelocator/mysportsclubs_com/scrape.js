const Apify = require('apify');

const {
  enqueueRegionClubPages,
} = require('./routes');

const {
  formatObject,
  formatAddress,
  formatHours,
  formatPhoneNumber,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.newyorksportsclubs.com/page/sitemap',
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
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 10,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await enqueueRegionClubPages(page, requestQueue, request);
      }
      if (request.userData.urlType === 'region') {
        await page.waitForSelector('script');
        const allScripts = await page.$$eval('script', se => se.map(s => s.innerText));
        const dataScript = allScripts.filter(e => e.includes('var clubs'));

        // Technically not all. All would double the amount but its a duplicate.
        const allTableBodies = await page.$$eval('#map-club-list tbody', te => te.map(t => t.innerText));
        const hourData = allTableBodies.filter(e => e.includes('AM'));

        if (dataScript) {
          const stringObject = dataScript[0];
          const arrayRaw = stringObject.substring(stringObject.indexOf('['), stringObject.indexOf(';'));
          const locationArray = formatObject(arrayRaw);

          /* eslint-disable no-restricted-syntax */
          for await (const [i, locationObject] of locationArray.entries()) {
            /* eslint-disable camelcase */
            const street_address = formatAddress(locationObject.address1, locationObject.address2);
            const hours_of_operation = formatHours(hourData[i]);
            const poiData = {
              locator_domain: 'mysportsclubs.com',
              location_name: locationObject.name,
              street_address,
              city: locationObject.city,
              state: locationObject.state,
              zip: locationObject.postcode,
              country_code: undefined,
              store_number: undefined,
              phone: formatPhoneNumber(locationObject.phone_number),
              location_type: undefined,
              latitude: locationObject.latitude,
              longitude: locationObject.longitude,
              hours_of_operation,
            };
            const poi = new Poi(poiData);
            await Apify.pushData(poi);
          }
        }
      }
    },
  });

  await crawler.run();
});
