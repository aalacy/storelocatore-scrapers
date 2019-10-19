const Apify = require('apify');

const {
  formatPhoneNumber,
  formatCountry,
  formatGeo,
} = require('./tools');

const {
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  countrySelector,
  locationTypeSelector,
  phoneSelector,
  geoSelector,
} = require('./selectors');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www3.hilton.com/sitemapurl-hi-00000.xml',
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
    maxRequestsPerCrawl: 1500,
    maxConcurrency: 10,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/www3.hilton.com\/en\/hotels\/(\w|-)+\/(\w|-)+\/index.html/))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
        await page.waitFor(5000);
      }
      if (request.userData.urlType === 'detail') {
        console.log(request.url);
        /* eslint-disable camelcase */
        await page.waitForSelector(countrySelector, { waitUntil: 'load', timeout: 0 });
        const countryRaw = await page.$eval(countrySelector, e => e.innerText);
        const country_code = formatCountry(countryRaw);
        // Only get US and Canada hotels
        if (country_code === 'US' || country_code === 'CA') {
          const location_name = await page.$eval(locationNameSelector, e => e.innerText);
          const street_address = await page.$eval(streetAddressSelector, e => e.innerText);
          const city = await page.$eval(citySelector, e => e.innerText);
          const state = await page.$eval(stateSelector, e => e.innerText);
          const zip = await page.$eval(zipSelector, e => e.innerText);
          const location_type = await page.$eval(locationTypeSelector, e => e.innerText);
          const phoneNumberRaw = await page.$eval(phoneSelector, e => e.innerText);
          const phone = formatPhoneNumber(phoneNumberRaw);
          const geoRaw = await page.$eval(geoSelector, e => e.content);
          const latLong = formatGeo(geoRaw);

          const poiData = {
            locator_domain: 'hilton.com',
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number: undefined,
            phone: formatPhoneNumber(phone),
            location_type,
            ...latLong,
            hours_of_operation: undefined,
          };
          const poi = new Poi(poiData);
          await Apify.pushData(poi);
        }
      }
    },
  });

  await crawler.run();
});
