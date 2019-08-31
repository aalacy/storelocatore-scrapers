const Apify = require('apify');

const {
  formatObject,
  formatPhoneNumber,
  formatAddress,
  formatHours,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.worldgym.com/sitemap.xml',
    userData: {
      urlType: 'initial',
    },
  });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/www.worldgym.com\/.*\/home/))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        await page.waitFor(5000);
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        await page.waitForSelector('script', { waitUntil: 'load', timeout: 0 });
        /* eslint-disable camelcase */
        const allScripts = await page.$$eval('script', se => se.map(s => s.innerText));
        const locationScript = allScripts.filter(e => e.includes('foundLocation =') && e.includes('$(function()'));
        const locationString = locationScript[0];
        const locationScriptClip = locationString.substring(locationString.indexOf('foundLocation'), locationString.length);
        let locationObjectRaw = locationScriptClip.substring(locationScriptClip.indexOf('{'), (locationScriptClip.indexOf('"MicroSiteUrl"') - 1));
        locationObjectRaw += '"Fix":"Fix"}';
        const locationObject = formatObject(locationObjectRaw);
        const hoursArray = await page.$$eval('.gymhourstab .readmore', se => se.map(s => s.innerText));
        const hoursRaw = hoursArray.join(', ');

        const address = formatAddress(locationObject.Line1, locationObject.Line2);
        const poiData = {
          locator_domain: 'worldgym_com',
          location_name: locationObject.LocationName,
          street_address: address,
          city: locationObject.City,
          state: locationObject.State,
          zip: locationObject.Postal,
          country_code: undefined,
          store_number: locationObject.LocationNumber,
          phone: formatPhoneNumber(locationObject.Phone),
          location_type: undefined,
          latitude: locationObject.Latitude,
          longitude: locationObject.Longitude,
          hours_of_operation: formatHours(hoursRaw),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 4,
    launchPuppeteerOptions: { headless: true },
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
        timeout: 0, waitUntil: 'load',
      }),
  });

  await crawler.run();
});
