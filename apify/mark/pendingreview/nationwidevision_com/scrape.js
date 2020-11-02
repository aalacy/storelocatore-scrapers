const Apify = require('apify');

const {
  locationNameSelector,
  geoUrlSelector,
  hoursSelector,
} = require('./selectors');

const {
  formatObject,
  parseGoogleMapsUrl,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteUrl = 'https://nationwidevision.com/sitemap.xml';

  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(siteUrl, {
    timeout: 0, waitUntil: 'load',
  });
  const allUrls = await p.$$eval('a', ae => ae.map(a => a.getAttribute('href')));
  const locationUrls = allUrls.filter(e => e !== null)
    .filter(e => e.match(/nationwidevision.com\/location\/(\w|-)+/))
    .filter((e) => {
      if (e.includes('vision') || e.includes('center')) {
        return true;
      }
      return false;
    });
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
      const allScripts = await page.$$eval('script', se => se.map(s => s.innerText));
      const [locationObjectRaw] = allScripts.filter(e => e.includes('addressLocality'));
      const locationObject = formatObject(locationObjectRaw);
      /* eslint-disable camelcase */
      const location_name = await page.$eval(locationNameSelector, s => s.innerText);
      const street_address = locationObject.address.streetAddress;
      const city = locationObject.address.addressLocality;
      const state = locationObject.address.addressRegion;
      const zip = locationObject.address.postalCode;
      const phone = locationObject.telephone;
      await page.waitForSelector(geoUrlSelector, { waitUntil: 'load', timeout: 30000 });
      const geoUrl = await page.$eval(geoUrlSelector, s => s.getAttribute('href'));
      const hoursRaw = await page.$eval(hoursSelector, s => s.innerText);
      const hours_of_operation = formatHours(hoursRaw);
      const { latitude, longitude } = parseGoogleMapsUrl(geoUrl);

      const poiData = {
        locator_domain: 'nationwidevision_com',
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
    maxRequestsPerCrawl: 150,
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
