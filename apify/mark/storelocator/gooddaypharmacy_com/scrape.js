const Apify = require('apify');

const {
  locationHrefSelector,
  addressBlockSelector,
  phoneSelector,
  hourSelector,
} = require('./selectors');

const {
  extractLocationInfo,
  formatPhoneNumber,
  parseGoogleMapsUrl,
  formatHours,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const initialUrl = 'https://www.gooddaypharmacy.com/locations';
  const baseUrl = 'https://www.gooddaypharmacy.com';
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
      if (await page.$(phoneSelector) !== null) {
        const addressBlock = await page.$(addressBlockSelector);
        const streetAddress = await addressBlock.$eval('ul li:nth-child(1)', e => e.innerText);
        const cityStateZip = await addressBlock.$eval('ul li:nth-child(2)', e => e.innerText);
        await page.waitForSelector(phoneSelector, { waitUntil: 'load', timeout: 30000 });
        const phoneRaw = await page.$eval(phoneSelector, e => e.innerText);
        const hourElement = await page.$(hourSelector);
        const hoursRaw = await hourElement.$eval('ul', e => e.innerText);
        const addressInfo = extractLocationInfo(streetAddress, cityStateZip);

        let googleFrame;
        /* eslint-disable no-restricted-syntax */
        for (const frame of page.mainFrame().childFrames()) {
          if (frame.url().includes('google')) {
            googleFrame = frame;
          }
        }
        /* eslint-disable dot-notation */
        const geoUrl = googleFrame['_url'];
        const latLong = parseGoogleMapsUrl(geoUrl);

        const poiData = {
          /* eslint-disable camelcase */
          locator_domain: 'gooddaypharmacy.com',
          ...addressInfo,
          phone: formatPhoneNumber(phoneRaw),
          ...latLong,
          hours_of_operation: formatHours(hoursRaw),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
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
