const Apify = require('apify');

const {
  locationHrefSelector,
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hourSelector,
  locationBlock,
  locationNameSelector2,
} = require('./selectors');

const {
  createGenericAddress,
  extractLocationInfo,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const initialUrl = 'https://www.greenmill.com/locations/';
  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(initialUrl, { waitUntil: 'networkidle0', timeout: 30000 });
  const locationLinks = await p.$$eval(locationHrefSelector, se => se.map(s => s.getAttribute('href')));
  const allRequests = locationLinks.map(e => ({ url: e }));

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
      // A few pages don't have the typical format, requires a dirty parse
      if (await page.$(locationNameSelector) !== null) {
        /* eslint-disable camelcase */
        const location_name = await page.$eval(locationNameSelector, e => e.innerText);
        const street_address = await page.$eval(streetAddressSelector, e => e.innerText);
        const city = await page.$eval(citySelector, e => e.innerText);
        const state = await page.$eval(stateSelector, e => e.innerText);
        const zip = await page.$eval(zipSelector, e => e.innerText);
        const phone = await page.$eval(phoneSelector, e => e.innerText);
        const latitude = await page.$eval(latitudeSelector, e => e.getAttribute('content'));
        const longitude = await page.$eval(longitudeSelector, e => e.getAttribute('content'));
        const hours_of_operation = await page.$eval(hourSelector, e => e.getAttribute('content'));

        const poiData = {
          locator_domain: 'greenmill.com',
          location_name,
          street_address,
          city,
          state,
          zip,
          phone,
          latitude,
          longitude,
          hours_of_operation,
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      } else if (await page.$(locationBlock) !== null) {
        const location_name = await page.$eval(locationNameSelector2, e => e.innerText);
        const infoBlockRaw = await page.$eval(locationBlock, e => e.innerHTML);
        const addressObject = createGenericAddress(infoBlockRaw);
        const { streetAddress, cityStateZip } = addressObject;
        const addressBlock = extractLocationInfo(streetAddress, cityStateZip);

        const poiData = {
          locator_domain: 'greenmill.com',
          location_name,
          ...addressBlock,
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
    maxRequestsPerCrawl: 50,
    maxConcurrency: 10,
    launchPuppeteerOptions: {
      headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy,
    },
    gotoFunction: async ({
      request, page,
    }) => {
      await page.goto(request.url, {
        timeout: 60000, waitUntil: 'networkidle0',
      });
    },
  });

  await crawler.run();
});
