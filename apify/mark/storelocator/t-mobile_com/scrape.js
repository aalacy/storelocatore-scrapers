const Apify = require('apify');

const {
  locationNameSelector,
  addressSelector,
  phoneSelector,
  hoursSelector,
} = require('./selectors');

const {
  formatObject,
  formatAddressOneLine,
  formatPhoneNumber,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.t-mobile.com/store-locator-sitemap.xml',
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
    maxRequestsPerCrawl: 6000,
    maxConcurrency: 10,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/https:\/\/www.t-mobile.com\/store-locator\/[a-z][a-z]\/(\w|-)+\/(\w|-)+/))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        await page.waitFor(5000);
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        if (await page.$('#schemaDataID') !== null) {
          let poiData;
          const locationObjectRaw = await page.$eval('#schemaDataID', e => e.innerText);
          // Means no JSON - ld formatted data so pull without
          if (locationObjectRaw === '' || locationObjectRaw.length === 0) {
            /* eslint-disable camelcase */
            const location_name = await page.$eval(locationNameSelector, e => e.innerText);
            const addressRaw = await page.$eval(addressSelector, e => e.innerText);
            const phoneRaw = await page.$eval(phoneSelector, e => e.innerText);
            const address = formatAddressOneLine(addressRaw);
            const phone = formatPhoneNumber(phoneRaw);
            poiData = {
              locator_domain: 't-mobile.com',
              location_name,
              ...address,
              phone,
            };
          } else {
            // Means JSON -ld is not empty
            const locationObject = formatObject(locationObjectRaw);
            /* eslint-disable camelcase */
            let hours_of_operation;
            if (await page.$(hoursSelector) !== null) {
              const hoursRaw = await page.$eval(hoursSelector, e => e.innerText);
              hours_of_operation = formatHours(hoursRaw);
            }
            poiData = {
              locator_domain: 't-mobile.com',
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
          }
          const poi = new Poi(poiData);
          await Apify.pushData(poi);
          await page.waitFor(3000);
        }
      }
    },
  });

  await crawler.run();
});
