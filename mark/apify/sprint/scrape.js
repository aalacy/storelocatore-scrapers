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
  formatData,
} = require('./tools');

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
    handlePageFunction: async ({ page }) => {
      if (await page.$(checkStoreExists) !== null) {
        await page.waitForSelector(locationNameSelector, { waitUntil: 'load', timeout: 0 });
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
        await page.waitForSelector(geoSelector, { waitUntil: 'load', timeout: 0 });
        const latitude = await page.$eval(geoSelector, e => e.dataset.lat);
        const longitude = await page.$eval(geoSelector, e => e.dataset.lon);
        await page.waitForSelector(hourSelector);
        const hoursRaw = await page.$eval(hourSelector, h => h.innerText);
        const hours_of_operation = formatHours(hoursRaw);

        const poi = {
          locator_domain: 'tuesdaymorning.com',
          location_name,
          street_address,
          city,
          state,
          zip,
          phone,
          country_code,
          location_type: 'Store',
          latitude,
          longitude,
          hours_of_operation,
        };
        await Apify.pushData(formatData(poi));
        await page.waitFor(5000);
      } else {
        await page.waitFor(5000);
        if (!requestList.isEmpty()) {
          await requestList.fetchNextRequest();
        }
      }
    },
    maxRequestsPerCrawl: 10000,
    maxConcurrency: 7,
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
      timeout: 0, waitUntil: 'load',
    }),
  });

  await crawler.run();
});
