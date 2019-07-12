const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');

const {
  locationNameSelector,
  checkStoreExists,
  checkAddress,
  streetSelector,
  street2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  countryCodeSelector,
  phoneSelector,
  geoSelector,
  hourSelector,
} = require('./selectors');

const {
  formatPhoneNumber,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const xml = await rp('https://www.sprint.com/locations/sitemap.xml');
  const $ = cheerio.load(xml);
  const urls = $('loc').map((i, e) => ({ url: $(e).text() })).toArray();
  const locationUrls = urls.filter(e => e.url.match(/https:\/\/www.sprint.com\/locations\/[a-z][a-z]\/(\w|-)+\/(\w|-)+/));

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
        timeout: 30000, waitUntil: 'networkidle0',
      });
    },
    maxRequestsPerCrawl: 10000,
    maxConcurrency: 7,
    handlePageFunction: async ({ page }) => {
      if (await page.$(checkStoreExists) !== null) {
        /* eslint-disable camelcase */
        const location_name = await page.$eval(locationNameSelector, e => e.innerText);
        let street_address;
        const locationAddressElements = await page.$$eval(checkAddress, h => h);

        // Some addresses have two lines for the address
        if (locationAddressElements.length === 2) {
          const street1 = await page.$eval(streetSelector, e => e.innerText);
          const street2 = await page.$eval(street2Selector, e => e.innerText);
          street_address = `${street1}, ${street2}`;
        }
        if (locationAddressElements.length === 1) {
          street_address = await page.$eval(streetSelector, e => e.innerText);
        }
        const city = await page.$eval(citySelector, e => e.innerText);
        const state = await page.$eval(stateSelector, e => e.innerText);
        const zip = await page.$eval(zipSelector, e => e.innerText);
        const country_code = await page.$eval(countryCodeSelector, e => e.innerText);
        const phoneNumberRaw = await page.$eval(phoneSelector, p => p.innerText);

        const phone = formatPhoneNumber(phoneNumberRaw);
        const latitude = await page.$eval(geoSelector, e => e.dataset.lat);
        const longitude = await page.$eval(geoSelector, e => e.dataset.lon);
        const hoursRaw = await page.$eval(hourSelector, h => h.innerText);
        const hours_of_operation = formatHours(hoursRaw);

        const poiData = {
          locator_domain: 'sprint.com',
          location_name,
          street_address,
          city,
          state,
          zip,
          phone,
          country_code,
          latitude,
          longitude,
          hours_of_operation,
        };

        const poi = new Poi(poiData);
        await Apify.pushData(poi);
        await page.waitFor(1000);
      }
    },
  });

  await crawler.run();
});
