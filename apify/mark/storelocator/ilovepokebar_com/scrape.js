const Apify = require('apify');

const {
  locationHrefSelector,
  streetAddressSelector,
  cityStateZipSelector,
  phoneSelector,
} = require('./selectors');

const {
  extractLocationInfo,
  formatPhoneNumber,
  parseGoogleMapsUrl,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const initialUrl = 'https://www.ilovepokebar.com/locations';
  const baseUrl = 'https://www.ilovepokebar.com';
  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(initialUrl, { waitUntil: 'networkidle0', timeout: 30000 });
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
      const streetAddress = await page.$eval(streetAddressSelector, e => e.innerText);
      const cityStateZip = await page.$eval(cityStateZipSelector, e => e.innerText);
      const phoneRaw = await page.$eval(phoneSelector, e => e.innerText);
      const addressBlock = extractLocationInfo(streetAddress, cityStateZip);

      let googleFrame;
      /* eslint-disable no-restricted-syntax */
      for (const frame of page.mainFrame().childFrames()) {
        if (frame.url().includes('google')) {
          googleFrame = frame;
        }
      }
      /* eslint-disable dot-notation */
      const geoUrl = await googleFrame.$eval('div.google-maps-link > a', e => e.getAttribute('href'));
      const latLong = parseGoogleMapsUrl(geoUrl);
      /* eslint-disable camelcase */
      const poiData = {
        locator_domain: 'ilovepokebar.com',
        ...addressBlock,
        phone: formatPhoneNumber(phoneRaw),
        ...latLong,
      };
      const poi = new Poi(poiData);
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
        timeout: 60000, waitUntil: 'networkidle0',
      });
    },
  });

  await crawler.run();
});
