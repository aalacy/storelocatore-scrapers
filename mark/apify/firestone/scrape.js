const Apify = require('apify');

const {
  formatObject,
  formatPhoneNumber,
  formatData,
} = require('./tools');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://local.firestonecompleteautocare.com/sitemap.xml',
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
        const locationUrls = urls.filter(e => e.match(/local.firestonecompleteautocare.com\//))
          .map(e => ({ url: e, userData: { urlType: 'state' } }));
        await page.waitFor(5000);
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'state') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/https:\/\/local.firestonecompleteautocare.com\/(\w|-)+\/(\w|-)+\/(?=.*[0-9])(?=.*[a-z])([a-z0-9_-]+)\//))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        await page.waitFor(5000);
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        if (await page.$('head > script') !== null) {
          await page.waitForSelector('head > script');
          const allScripts = await page.$$eval('head > script', se => se.map(s => s.innerText));
          const indexContainingLocation = allScripts.findIndex(e => e.includes('streetAddress'));
          if (indexContainingLocation !== -1) {
            const locationObjectRaw = allScripts[indexContainingLocation];
            const locationObject = formatObject(locationObjectRaw);
            const poi = {
              locator_domain: 'firestonecompleteautocare.com',
              location_name: locationObject.name,
              street_address: locationObject.address.streetAddress,
              city: locationObject.address.addressLocality,
              state: locationObject.address.addressRegion,
              zip: locationObject.address.postalCode,
              country_code: locationObject.address.addressCountry,
              store_number: locationObject.branchCode,
              phone: formatPhoneNumber(locationObject.telephone),
              location_type: locationObject['@type'],
              naics_code: undefined,
              latitude: locationObject.geo.latitude,
              longitude: locationObject.geo.longitude,
              hours_of_operation: locationObject.openingHoursSpecification,
            };
            await Apify.pushData(formatData(poi));
            await page.waitFor(7000);
          } else {
            await page.waitFor(5000);
            if (requestQueue.isEmpty()) {
              await requestQueue.fetchNextRequest();
            }
          }
        } else {
          await page.waitFor(5000);
          if (requestQueue.isEmpty()) {
            await requestQueue.fetchNextRequest();
          }
        }
      }
    },
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 3,
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
      timeout: 0, waitUntil: 'networkidle0',
    }),
  });

  await crawler.run();
});
