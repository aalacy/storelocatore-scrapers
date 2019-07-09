const Apify = require('apify');
const { formatPhoneNumber, formatData } = require('./tools');

Apify.main(async () => {
  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto('https://stores.chicos.com/en/sitemap.xml');
  await p.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
  const urls = await p.$$eval('span', se => se.map(s => s.innerText));
  const storeUrls = urls.filter(e => e.match(/stores.chicos.com\/s\//)).map(e => ({ url: e }));

  const requestList = new Apify.RequestList({
    sources: storeUrls,
  });
  await requestList.initialize();

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
		launchPuppeteerOptions: {
      headless: true,
    },
		handlePageFunction: async ({ page }) => {
      await page.waitForSelector('head > script:nth-child(172)', { timeout: 0 });
      const scriptText = await page.$eval('head > script:nth-child(172)', s => s.innerText);
      const storeObject = JSON.parse(scriptText);

      const poi = {
        locator_domain: 'www.chicos.com__store__',
        location_name: storeObject.name,
        street_address: storeObject.address.streetAddress,
        city: storeObject.address.addressLocality,
        state: storeObject.address.addressRegion,
        zip: storeObject.address.postalCode,
        country_code: storeObject.address.addressCountry,
        store_number: undefined,
        phone: formatPhoneNumber(storeObject.telephone),
        location_type: 'Store',
        naics_code: undefined,
        latitude: storeObject.geo.latitude,
        longitude: storeObject.geo.longitude,
        hours_of_operation: storeObject.openingHoursSpecification,
      };

      await Apify.pushData(formatData(poi));
    },
    maxRequestsPerCrawl: 100,
    maxConcurrency: 4,
  });

  await crawler.run();
});
