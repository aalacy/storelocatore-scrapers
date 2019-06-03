const Apify = require('apify');

const {
  formatPhoneNumber,
  formatHours,
  formatData,
  parseAddress,
} = require('./tools');

Apify.main(async () => {
  const browser = await Apify.launchPuppeteer({ headless: false });
  const p = await browser.newPage();
  await p.goto('https://thehumanbean.com/sitemap/', { waitUntil: 'load', timeout: 0 });
  await p.waitFor(5000);
  const pageUrls = await p.$$eval('a', ae => ae.map(a => a.href));
  const reqUrls = pageUrls.filter(e => e.match(/(thehumanbean.com\/location\/)/))
    .map(e => ({ url: e }));
  await browser.close();

  const requestList = new Apify.RequestList({
    sources: reqUrls,
  });
  await requestList.initialize();

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ request, page }) => {
      await page.waitFor(7000);
      const dataSelector = 'body > div.site-container > div.site-inner > div > div > div > div > div > div > div > div > div > div > script';
      await page.waitForSelector(dataSelector);
      const storeData = await page.$eval(dataSelector, s => s.innerText);

      // Get the hours from the page
      let hourData;
      let fixedData;
      if (storeData.includes('openingHoursSpecification')) {
        const hourSelector = '#location-about > div > div > div > div > div > div > div > div > ul';
        await page.waitForSelector(hourSelector);
        hourData = await page.$eval(hourSelector, h => h.innerText);

        // Server provides faulty ld-json data so we clean it
        const trimmedData = storeData.trim().replace(/ +/g, ' ');
        const dataSubset = trimmedData.substring(0, (trimmedData.indexOf('openingHoursSpecification') - 5));
        fixedData = `${dataSubset}}`;
      }

      // Server provides faulty ld-json data so we clean it
      if (!storeData.includes('openingHoursSpecification')) {
        const trimmedData = storeData.trim().replace(/ +/g, ' ');
        const dataSubset = trimmedData.substring(0, (trimmedData.indexOf(']') - 3));
        fixedData = `${dataSubset}}`;
      }

      const storeObject = JSON.parse(fixedData);

      // Some sites have empty ld-json strings, so we have to parse the page for info
      if (storeObject.address.streetAddress.length < 2) {
        const titleSelector = 'body > div > div > div > div > div > div > div > div > div > div > div > h1 > span';
        await page.waitForSelector(titleSelector);
        const titleData = await page.$eval(titleSelector, t => t.innerText);
        const addressInfo = parseAddress(titleData);
        storeObject.address.streetAddress = addressInfo.streetAddress;
        storeObject.address.addressLocality = addressInfo.addressLocality;
        storeObject.address.addressRegion = addressInfo.addressRegion;
        storeObject.address.postalCode = addressInfo.zip;
      }

      const poi = {
        locator_domain: 'thehumanbean__com',
        location_name: undefined,
        street_address: storeObject.address.streetAddress,
        city: storeObject.address.addressLocality,
        state: storeObject.address.addressRegion,
        zip: storeObject.address.postalCode,
        country_code: storeObject.address.addressCountry,
        store_number: undefined,
        phone: formatPhoneNumber(storeObject.telephone),
        location_type: storeObject['@type'],
        naics_code: undefined,
        latitude: storeObject.geo.latitude,
        longitude: storeObject.geo.longitude,
        hours_of_operation: formatHours(hourData),
      };

      await Apify.pushData(formatData(poi));
    },
    launchPuppeteerOptions: { headless: false },
    maxRequestsPerCrawl: 100,
    maxConcurrency: 1,
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
        timeout: 0, waitUntil: 'load',
      }),
  });

  await crawler.run();
});
