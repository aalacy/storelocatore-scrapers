const Apify = require('apify');
const {
  locationInfoSelector,
} = require('./selectors');

const {
  formatGeoLocation,
  formatInfoBlock,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const baseUrl = 'http://www.navarro.com/';
  const dataStorage = await Apify.openKeyValueStore('visitedUrls');
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'http://www.navarro.com/store-locator.htm',
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
    maxRequestsPerCrawl: 10,
    maxConcurrency: 1,
    handlePageFunction: async ({ request, page }) => {
      await page.waitForSelector(locationInfoSelector);
      const allPageInfo = await page.$$eval(locationInfoSelector, le => le.map(l => l.innerText));

      // We use this twice once to receive coordinates and below to get the next Button
      const allButtonOnclickProperties = await page.$$eval('button', nb => nb.map(b => b.getAttribute('onclick')));
      let geoLocs;
      // Geo coordinates appear to display only on the first page buttons, but switch to span
      if (request.userData.urlType === 'initial') {
        geoLocs = allButtonOnclickProperties.filter(e => e && e.includes('findLocation'));
      }
      // Geo Coordinates suddenly appear on span on clicks
      if (request.userData.urlType === 'nextPage') {
        const allSpansOnClickProperties = await page.$$eval('span', se => se.map(s => s.getAttribute('onclick')));
        geoLocs = allSpansOnClickProperties.filter(e => e && e.includes('findLocation'));
      }
      /* eslint-disable no-restricted-syntax */
      for await (const [i, locationInfo] of allPageInfo.entries()) {
        const latLong = formatGeoLocation(geoLocs[i]);
        const primaryInfo = formatInfoBlock(locationInfo);
        const poiData = {
          locator_domain: 'navarro.com',
          ...primaryInfo,
          country_code: undefined,
          location_type: undefined,
          ...latLong,
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }

      // The next button can change locations so we find all buttons and look for next
      await page.waitForSelector('button', { waitUntil: 'load', timeout: 0 });
      const allButtons = await page.$$eval('button', be => be.map(b => b.innerText));
      const nextButtonIndex = allButtons.findIndex(e => e.includes('Next'));
      const nextButtonOnClickProp = allButtonOnclickProperties[nextButtonIndex];
      const nextPageUrlRaw = nextButtonOnClickProp.substring((nextButtonOnClickProp.indexOf('\'') + 1), (nextButtonOnClickProp.length - 1));
      const nextPageUrl = baseUrl + nextPageUrlRaw;

      await page.waitFor(8000);
      // The site loops its urls, so we check to ensure we haven't visited it already
      if (await dataStorage.getValue(nextPageUrlRaw) === null) {
        await dataStorage.setValue(nextPageUrlRaw, { requestAdded: nextPageUrl });
        await requestQueue.addRequest({
          url: nextPageUrl,
          userData: {
            urlType: 'nextPage',
          },
        });
      }
    },
  });

  await crawler.run();
});
