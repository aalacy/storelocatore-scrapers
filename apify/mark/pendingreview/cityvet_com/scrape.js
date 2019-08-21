const Apify = require('apify');

const {
  locationNameSelector,
  addressSelector,
  phoneSelector,
  geoUrlSelector,
  hoursSelector,
} = require('./selectors');

const {
  parseAddress,
  parseGoogleMapsUrl,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteUrl = 'https://www.cityvet.com/sitemap.xml';

  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(siteUrl, {
    timeout: 0, waitUntil: 'load',
  });
  const allUrls = await p.$$eval('span', ae => ae.map(a => a.innerText));
  const locationUrls = allUrls.filter(e => e !== null)
    .filter(e => !e.includes('.pdf'))
    .filter(e => !e.includes('.php'))
    .filter(e => e.match(/www.cityvet.com\/[a-z](\w|-)+/));
  const adjustedUrls = locationUrls.map(e => ({ url: `${e}` }));
  await browser.close();

  const requestList = new Apify.RequestList({
    sources: adjustedUrls,
  });
  await requestList.initialize();

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ page }) => {
      /* eslint-disable camelcase */
      const location_name = await page.$eval(locationNameSelector, s => s.innerText);
      const addressBlockRaw = await page.$eval(addressSelector, s => s.innerText);
      const phone = await page.$eval(phoneSelector, s => s.innerText);
      const geoUrl = await page.$eval(geoUrlSelector, s => s.getAttribute('href'));
      const hoursRaw = await page.$eval(hoursSelector, s => s.innerText);
      const hours_of_operation = formatHours(hoursRaw);
      const { latitude, longitude } = parseGoogleMapsUrl(geoUrl);
      const {
        street_address, city, state, zip,
      } = parseAddress(addressBlockRaw);

      const poiData = {
        locator_domain: 'cityvet_com',
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
    },
    maxRequestsPerCrawl: 20,
    maxConcurrency: 10,
    launchPuppeteerOptions: {
      headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy,
    },
  });

  await crawler.run();
});
