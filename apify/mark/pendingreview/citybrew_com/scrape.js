const Apify = require('apify');

const {
  addressPhoneBlockSelector,
  phoneSelector2,
  hoursSelector,
  hoursSelector2,
} = require('./selectors');

const {
  parseAddress,
  parseGoogleMapsUrl,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteUrl = 'https://citybrew.com/locations/';
  const baseUrl = 'https://citybrew.com';

  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(siteUrl, {
    timeout: 0, waitUntil: 'load',
  });
  const allUrls = await p.$$eval('a', ae => ae.map(a => a.getAttribute('href')));
  const locationUrls = allUrls.filter(e => e !== null)
    .filter(e => e.match(/\/locations\/(\w|-)+\//));
  const adjustedUrls = locationUrls.map(e => ({ url: `${baseUrl}${e}` }));
  await browser.close();

  const requestList = new Apify.RequestList({
    sources: adjustedUrls,
  });
  await requestList.initialize();

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ request, page }) => {
      /* eslint-disable camelcase */
      let phone;
      const addressPhoneBlockRaw = await page.$eval(addressPhoneBlockSelector, s => s.innerText);
      const {
        street_address, city, state, zip,
      } = parseAddress(addressPhoneBlockRaw);
      ({ phone } = parseAddress(addressPhoneBlockRaw));
      let hours_of_operation;
      if (await page.$(hoursSelector) !== null) {
        const hoursRaw = await page.$eval(hoursSelector, s => s.innerText);
        hours_of_operation = formatHours(hoursRaw);
      } else {
        phone = await page.$eval(phoneSelector2, s => s.innerText);
        const hoursRaw = await page.$eval(hoursSelector2, s => s.innerText);
        hours_of_operation = formatHours(hoursRaw);
      }

      let googleFrame;
      /* eslint-disable no-restricted-syntax */
      for (const frame of page.mainFrame().childFrames()) {
        if (frame.url().includes('google')) {
          googleFrame = frame;
        }
      }
      /* eslint-disable dot-notation */
      let latitude;
      let longitude;
      if (await googleFrame.$('div.google-maps-link > a') !== null) {
        const geoUrl = await googleFrame.$eval('div.google-maps-link > a', e => e.getAttribute('href'));
        ({ latitude, longitude } = parseGoogleMapsUrl(geoUrl));
      } else {
        const geoUrl = await page.$eval('iframe', e => e.getAttribute('src'));
        ({ latitude, longitude } = parseGoogleMapsUrl(geoUrl));
      }
      const poiData = {
        locator_domain: 'citybrew_com',
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
