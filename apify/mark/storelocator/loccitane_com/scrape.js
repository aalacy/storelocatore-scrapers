const Apify = require('apify');
const {
  formatPhoneNumber, formatGeoString, removeEmptyStrings,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

const loccitaneUS = 'https://usa.loccitane.com/doc/GlobalCache/OCC/SiteMaps/Sitemap_Stores_82.xml';
const loccitaneCA = 'https://ca.loccitane.com/doc/GlobalCache/OCC/SiteMaps/Sitemap_Stores_19.xml';

Apify.main(async () => {
  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.setJavaScriptEnabled(true);
  await p.goto(loccitaneUS, { waitUntil: 'load', timeout: 0 });
  await p.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
  const urls = await p.$$eval('span', se => se.map(s => s.innerText));
  const usStoreUrls = urls.filter(e => e.match(/usa.loccitane.com\/bp\//)).map(e => ({ url: e }));
  await p.waitFor(5000);

  // Open a new page to get Canada links
  const p2 = await browser.newPage();
  await p2.goto(loccitaneCA, { waitUntil: 'load', timeout: 0 });
  await p2.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
  const caUrls = await p2.$$eval('span', se => se.map(s => s.innerText));
  // We're filtering out if the location starts with non alphabet
  // We're also filtering for English only versions of the site (19,2 -> French version)
  const caStoreUrls = caUrls.filter(e => e.match(/ca.loccitane.com\/bp\/[A-Z]/) && e.includes('19,1'))
    .map(e => ({ url: e }));
  await p.waitFor(5000);
  const reqUrls = [...usStoreUrls, ...caStoreUrls];
  await browser.close();

  const requestList = new Apify.RequestList({
    sources: reqUrls,
  });
  await requestList.initialize();

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    launchPuppeteerOptions: {
      headless: false,
      useChrome: true,
			stealth: true,
			headless: true
    },
    gotoFunction: async ({
      request, page,
    }) => {
      await page.goto(request.url, {
        timeout: 0, waitUntil: 'networkidle0',
      });
    },
    maxRequestsPerCrawl: 600,
    maxConcurrency: 1,
    handlePageFunction: async ({ page }) => {
      await page.setJavaScriptEnabled(true);
      await page.waitForSelector('#content > script:nth-child(3)', { waitUntil: 'networkIdle0', timeout: 0 });
      const scriptText = await page.$eval('#content > script:nth-child(3)', s => s.innerText);
      const stringObject = scriptText.substring(scriptText.indexOf('{'), scriptText.indexOf(';'));

      const storeObject = JSON.parse(stringObject);

      const poiData = {
        locator_domain: 'loccitane.com',
        location_name: storeObject.Name,
        street_address: storeObject.Address1,
        city: storeObject.City,
        state: storeObject.State,
        zip: storeObject.ZipCode,
        country_code: storeObject.ISO2,
        store_number: storeObject.Id,
        phone: formatPhoneNumber(storeObject.Phone),
        ...((storeObject.IsSpa === false, storeObject.IsRetailer === true) && { location_type: 'Spa' }),
        ...((storeObject.IsSpa === false, storeObject.IsRetailer === false) && { location_type: 'Store' }),
        naics_code: undefined,
        ...formatGeoString(storeObject.Latlong),
        hours_of_operation: storeObject.RegularOpeningHours,
      };
      const cleanPoiData = removeEmptyStrings(poiData);
      const poi = new Poi(cleanPoiData);
      await Apify.pushData(poi);
      await page.waitFor(5000);
    },
  });
  await crawler.run();
});
