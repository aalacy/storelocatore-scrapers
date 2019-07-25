const Apify = require('apify');

const {
  locationHrefSelector,
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  geoUrlSelector,
  hourSelector,
} = require('./selectors');

const {
  parseGeoUrl,
  removeEmptyStringProperties,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const baseUrl = 'https://www.lovesac.com';
  const initialUrl = 'https://www.lovesac.com/store-locator/show-all-locations';
  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(initialUrl, { waitUntil: 'load', timeout: 30000 });
  const locationLinks = await p.$$eval(locationHrefSelector, se => se.map(s => s.getAttribute('href')));
  const allRequests = locationLinks.map(e => ({ url: `${baseUrl}${e}` }));
  const requestList = new Apify.RequestList({
    sources: allRequests,
  });
  await requestList.initialize();
  await browser.close();

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({
      page,
    }) => {
      /* eslint-disable camelcase */
      const location_name = await page.$eval(locationNameSelector, e => e.innerText);
      const street_address = await page.$eval(streetAddressSelector, e => e.innerText);
      const city = await page.$eval(citySelector, e => e.innerText);
      const state = await page.$eval(stateSelector, e => e.innerText);
      const zip = await page.$eval(zipSelector, e => e.innerText);
      const phone = await page.$eval(phoneSelector, e => e.innerText);
      await page.waitForSelector(geoUrlSelector, { waitUntil: 'load', timeout: 10000 });
      const geoUrl = await page.$eval(geoUrlSelector, e => e.getAttribute('href'));
      const hours = await page.$$eval(hourSelector, se => se.map(e => e.getAttribute('datetime')));
      const hours_of_operation = hours.join(', ');
      const latLong = parseGeoUrl(geoUrl);

      const poiData = {
        locator_domain: 'lovesac.com',
        location_name,
        street_address,
        city,
        state,
        zip,
        phone,
        ...latLong,
        hours_of_operation,
      };
      const cleanPoiData = removeEmptyStringProperties(poiData);
      const poi = new Poi(cleanPoiData);
      await Apify.pushData(poi);
    },
    maxRequestsPerCrawl: 100,
    maxConcurrency: 10,
    launchPuppeteerOptions: {
      headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy,
    },
    gotoFunction: async ({
      request, page,
    }) => {
      await page.goto(request.url, {
        timeout: 60000, waitUntil: 'load',
      });
    },
  });

  await crawler.run();
});
