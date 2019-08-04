const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');

const {
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  addressBlockSelector,
  phoneSelector,
  geoUrlSelector,
  hourSelector,
} = require('./selectors');

const {
  formatLocationName,
  extractZipCode,
  formatPhoneNumber,
  parseGoogleMapsUrl,
  formatHours,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

const locationSitemap = 'https://www.gatewayacademy.com/sitemaps/school-minisites-3.xml';

Apify.main(async () => {
  // Get list of urls from store locator sitemap
  const xml = await rp(locationSitemap);
  const $c = cheerio.load(xml);
  const allurls = $c('loc').map((i, e) => ({ url: $c(e).text() })).toArray();
  const urls = allurls.filter(e => e.url.match(/gatewayacademy.com\/schools\/(\w|-)+-preschool\/$/));

  const requestList = new Apify.RequestList({
    sources: urls,
  });
  await requestList.initialize();

  const useProxy = process.env.USE_PROXY;

  /* eslint-disable no-unused-vars */
  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ request, page }) => {
      /* eslint-disable camelcase */
      const locationNameRaw = await page.$eval(locationNameSelector, e => e.innerText);
      const street_address = await page.$eval(streetAddressSelector, e => e.innerText);
      const city = await page.$eval(citySelector, e => e.innerText);
      const state = await page.$eval(stateSelector, e => e.innerText);
      const addressBlock = await page.$eval(addressBlockSelector, e => e.innerText);
      const zip = extractZipCode(addressBlock);
      const phoneRaw = await page.$eval(phoneSelector, e => e.innerText);
      const geoUrl = await page.$eval(geoUrlSelector, e => e.getAttribute('href'));
      const hoursRaw = await page.$eval(hourSelector, e => e.innerText);

      const latLong = parseGoogleMapsUrl(geoUrl);

      const poiData = {
        locator_domain: 'gatewayacademy.com',
        location_name: formatLocationName(locationNameRaw),
        street_address,
        city,
        state,
        ...zip,
        phone: formatPhoneNumber(phoneRaw),
        ...latLong,
        hours_of_operation: formatHours(hoursRaw),
      };

      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
    maxRequestsPerCrawl: 500,
    maxConcurrency: 10,
    maxRequestRetries: 1,
    handlePageTimeoutSecs: 60,
    launchPuppeteerOptions: {
      headless: true,
      stealth: true,
      useChrome: true,
      useApifyProxy: !!useProxy,
    },
  });

  await crawler.run();
});
