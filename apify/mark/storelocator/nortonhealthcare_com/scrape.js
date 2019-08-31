const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');

const {
  hourSelector,
} = require('./selectors');

const {
  formatObject,
  formatName,
  formatPhoneNumber,
  extractLocationType,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteMapUrl = 'https://nortonhealthcare.com/hospital-sitemap.xml';
  const xml = await rp(siteMapUrl);
  const $c = cheerio.load(xml);
  const urls = $c('loc').map((i, e) => ({ url: $c(e).text() })).toArray();

  const requestList = new Apify.RequestList({
    sources: urls,
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
    maxRequestsPerCrawl: 550,
    maxConcurrency: 10,
    handlePageFunction: async ({ page }) => {
      await page.waitForSelector('script', { timeout: 0, waitUntil: 'load' });
      const allScripts = await page.$$eval('script', se => se.map(s => s.innerText));
      const locationScriptArray = allScripts.filter(e => e.includes('GeoCoordinates'));
      const locationScriptString = locationScriptArray[0];
      const locationObjectPre = locationScriptString.substring('{', locationScriptString.length);
      const locationObjectRaw = locationObjectPre.substring(0, (locationObjectPre.lastIndexOf('}') - 1));
      const locationObject = formatObject(locationObjectRaw);
      const hoursArray = await page.$$eval(hourSelector, se => se.map(e => e.innerText));

      const poiData = {
        locator_domain: 'nortonhealthcare.com',
        location_name: formatName(locationObject.name),
        street_address: locationObject.address.streetAddress,
        city: locationObject.address.addressLocality,
        state: locationObject.address.addressRegion,
        zip: locationObject.address.postalCode,
        country_code: locationObject.address.addressCountry,
        store_number: undefined,
        phone: formatPhoneNumber(locationObject.telephone),
        location_type: extractLocationType(locationObject.url),
        latitude: locationObject.geo.latitude,
        longitude: locationObject.geo.longitude,
        hours_of_operation: formatHours(hoursArray),
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
  });

  await crawler.run();
});
