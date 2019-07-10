const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');

const {
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hourSelector,
} = require('./selectors');

const {
  formatHours,
  formatPhoneNumber,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  // Cheerio crawler is unable to load .xml sites, so we preload the site.
  const siteMapUrl = 'https://static1.st8fm.com/en_US/pod_content/www/sitemap-agents.xml';
  const xml = await rp(siteMapUrl);
  const $c = cheerio.load(xml);
  const urls = $c('loc').map((i, e) => ({ url: $c(e).text() })).toArray();

  const locationUrls = urls.filter(e => e.url.match(/www.statefarm.com\/agent\/us\/[a-z][a-z]\/.*\//));

  const requestList = new Apify.RequestList({
    sources: locationUrls,
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
    maxConcurrency: 1,
    handlePageFunction: async ({
      page,
    }) => {
      /* eslint-disable camelcase */
      await page.waitFor(5000);
      const location_name = await page.$eval(locationNameSelector, e => e.innerText);
      const street_address = await page.$eval(streetAddressSelector, e => e.innerText);
      const city = await page.$eval(citySelector, e => e.innerText);
      const state = await page.$eval(stateSelector, e => e.innerText);
      const zip = await page.$eval(zipSelector, e => e.innerText);
      const phone = await page.$eval(phoneSelector, e => e.innerText);
      const latitude = await page.$eval(latitudeSelector, e => e.getAttribute('value'));
      const longitude = await page.$eval(longitudeSelector, e => e.getAttribute('value'));
      const hours = await page.$eval(hourSelector, e => e.innerText);

      const poiData = {
        locator_domain: 'statefarm.com',
        location_name,
        street_address,
        city,
        state,
        zip,
        country_code: undefined,
        phone: formatPhoneNumber(phone),
        latitude,
        longitude,
        hours_of_operation: formatHours(hours),
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
  });

  await crawler.run();
});
