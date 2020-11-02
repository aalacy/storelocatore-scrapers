const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');
const zlib = require('zlib');
const util = require('util');

const zlibUnzip = util.promisify(zlib.unzip);

const {
  locationNameSelector,
  streetAddressSelector,
  phoneSelector,
  hoursSelector,
  geoUrlSelector,
} = require('./selectors');

const {
  parseAddress,
  parseGoogleMapsUrl,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteMapUrl = 'https://www.hobbytown.com/sitemapstore-locations-1.xml.gz';

  const responseBody = await rp.get({
    uri: siteMapUrl,
    gzip: true,
    encoding: null,
  });

  const xmlRaw = await zlibUnzip(responseBody);
  const xml = xmlRaw.toString();
  const $ = cheerio.load(xml);
  const urls = $('loc').map((i, e) => ({ url: $(e).text() })).toArray();

  const requestList = new Apify.RequestList({
    sources: urls,
  });
  await requestList.initialize();

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ page }) => {
      /* eslint-disable camelcase */
      const location_name = await page.$eval(locationNameSelector, e => e.innerText);
      const addressBlock = await page.$eval(streetAddressSelector, e => e.innerText);
      const phone = await page.$eval(phoneSelector, e => e.innerText);
      await page.waitForSelector(geoUrlSelector, { waitUntil: 'load', timeout: 30000 });
      const geoUrl = await page.$eval(geoUrlSelector, e => e.getAttribute('href'));
      const hoursRaw = await page.$eval(hoursSelector, e => e.innerText);
      const hours_of_operation = formatHours(hoursRaw);
      const {
        street_address, city, state, zip,
      } = parseAddress(addressBlock);
      const { latitude, longitude } = parseGoogleMapsUrl(geoUrl);

      const poiData = {
        locator_domain: 'hobbytown_com',
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
    maxRequestsPerCrawl: 180,
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
