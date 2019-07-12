const Apify = require('apify');

const {
  formatObject,
  formatPhoneNumber,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

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
    maxRequestsPerCrawl: 1800,
    maxConcurrency: 10,
    handlePageFunction: async ({
      request, page, skipLinks,
      skipOutput,
    }) => {
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/local.firestonecompleteautocare.com\//))
          .map(e => ({ url: e, userData: { urlType: 'state' } }));
        await page.waitFor(3000);
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
        await page.waitFor(3000);
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
            const hoursArray = locationObject.openingHoursSpecification;
            const hoursArrayFix = hoursArray.map((e) => {
              const dayOfWeek = e.dayOfWeek.replace('http://schema.org/', '');
              return `${dayOfWeek} ${e.opens}: ${e.closes}`;
            });
            /* eslint-disable camelcase */
            const hours_of_operation = hoursArrayFix.join(', ');
            const poiData = {
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
              latitude: locationObject.geo.latitude,
              longitude: locationObject.geo.longitude,
              hours_of_operation,
            };
            const poi = new Poi(poiData);
            await Apify.pushData(poi);
          } else {
            await skipOutput();
            await skipLinks();
          }
        } else {
          await skipOutput();
          await skipLinks();
        }
      }
    },
  });

  await crawler.run();
});
