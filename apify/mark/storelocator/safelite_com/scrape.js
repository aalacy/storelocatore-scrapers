const Apify = require('apify');
const {
  locationExistsSelector,
  locationNameSelector,
  streetAddressSelector,
  cityStateZipSelector,
  phoneSelector,
  hoursExistsSelector,
  hourSelector,
  googleMapsUrlSelector,
} = require('./selectors');

const {
  formatPhoneNumber,
  formatAddress,
  formatHours,
  parseGoogleMapsUrl,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.safelite.com/sitemap.xml',
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
    maxRequestsPerCrawl: 20000,
    maxConcurrency: 10,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/safelite.com\/stores\//))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        await page.waitFor(5000);
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        // Some pages have no address, so check if it exists
        if (await page.$(locationExistsSelector) !== null) {
          const possibleStoreElement = await page.$eval(locationExistsSelector, e => e.innerText);
          // Some stores have a location selector, but are mobile vans
          if (possibleStoreElement.includes('Store address')) {
            await page.waitForSelector(locationNameSelector, { waitUntil: 'load', timeout: 0 });
            /* eslint-disable camelcase */
            const location_name = await page.$eval(locationNameSelector, h => h.innerText);
            await page.waitFor(1000);

            const street_address = await page.$eval(streetAddressSelector, a => a.innerText);
            const addressLine2 = await page.$eval(cityStateZipSelector, a2 => a2.innerText);
            const phoneNumberRaw = await page.$eval(phoneSelector, p => p.innerText);
            const cityStateZip = formatAddress(addressLine2);

            const phone = formatPhoneNumber(phoneNumberRaw);

            let hours_of_operation;
            if (await page.$(hoursExistsSelector) !== null) {
              const hoursRaw = await page.$eval(hourSelector, h => h.innerText);
              hours_of_operation = formatHours(hoursRaw);
            }

            await page.waitForSelector(googleMapsUrlSelector, { waitUntil: 'load', timeout: 0 });
            const googleMapsUrl = await page.$eval(googleMapsUrlSelector, a => a.href);
            const latLong = parseGoogleMapsUrl(googleMapsUrl);

            const poiData = {
              locator_domain: 'safelite.com',
              location_name,
              street_address,
              ...cityStateZip,
              country_code: undefined,
              phone,
              ...latLong,
              hours_of_operation,
            };
            const poi = new Poi(poiData);
            await Apify.pushData(poi);
            await page.waitFor(2000);
          }
        }
      }
    },
  });

  await crawler.run();
});
