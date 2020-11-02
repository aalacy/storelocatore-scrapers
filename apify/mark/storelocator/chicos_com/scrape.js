const Apify = require('apify');
const {
  formatPhoneNumber,
  formatObject,
  formatHours,
} = require('./tools');
const { Poi } = require('./Poi');

Apify.main(async () => {
  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto('https://stores.chicos.com/en/sitemap.xml');
  await p.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
  const urls = await p.$$eval('span', se => se.map(s => s.innerText));
  const storeUrls = urls.filter(e => e.match(/stores.chicos.com\/s\//)).map(e => ({ url: e }));
  await p.waitFor(5000);

  const requestList = new Apify.RequestList({
    sources: storeUrls,
  });
  await requestList.initialize();

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
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
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 10,
    handlePageFunction: async ({ page }) => {
      await page.waitForSelector('script', { waitUntil: 'load', timeout: 0 });
      const scriptText = await page.$$eval('script', se => se.map(s => s.innerText));
      await page.waitForSelector('.bw__BusinessHours', { waitUntil: 'load', timeout: 0 });
      const hourText = await page.$eval('.bw__BusinessHours', s => s.innerText);
      const storeObjectArray = scriptText.filter(e => e.includes('GeoCoordinates'));
      const storeObjectRaw = storeObjectArray[0];
      const storeObject = formatObject(storeObjectRaw);
      /* eslint-disable camelcase */
      const hours_of_operation = formatHours(hourText);

      const poiData = {
        locator_domain: 'www.chicos.com__store__',
        location_name: storeObject.name,
        street_address: storeObject.address.streetAddress,
        city: storeObject.address.addressLocality,
        state: storeObject.address.addressRegion,
        zip: storeObject.address.postalCode,
        country_code: storeObject.address.addressCountry,
        store_number: undefined,
        phone: formatPhoneNumber(storeObject.telephone),
        location_type: storeObject['@type'],
        latitude: storeObject.geo.latitude,
        longitude: storeObject.geo.longitude,
        hours_of_operation,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
  });

  await crawler.run();
});
