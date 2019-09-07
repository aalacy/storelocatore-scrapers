const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');

const {
  locationNameSelector,
  storeNumberSelector,
  streetSelector,
  street2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  countrySelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hourSelector,
} = require('./selectors');

const {
  formatPhoneNumber,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const xml = await rp('http://www.tuesdaymorning.com/stores/sitemap.xml');
  const $ = cheerio.load(xml);
  const urls = $('loc').map((i, e) => ({ url: $(e).text() })).toArray();
  const locationUrls = urls.filter(e => e.url.match(/https:\/\/www.tuesdaymorning.com\/stores\/.*\/.*\/[0-9].*.html/));

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
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 10,
    handlePageFunction: async ({ page }) => {
      /* eslint-disable camelcase */
      const location_name = await page.$eval(locationNameSelector, e => e.innerText);
      const store_number = await page.$eval(storeNumberSelector, h => h.innerText);

      let street_address = await page.$eval(streetSelector, e => e.innerText);
      // Some addresses have two lines for the address
      if (await page.$(street2Selector) !== null) {
        const streetAddress2 = await page.$eval(street2Selector, e => e.innerText);
        street_address += `, ${streetAddress2}`;
      }

      const city = await page.$eval(citySelector, e => e.innerText);
      const state = await page.$eval(stateSelector, e => e.innerText);
      const zip = await page.$eval(zipSelector, e => e.innerText);
      const country_code = await page.$eval(countrySelector, e => e.innerText);
      const phoneNumberRaw = await page.$eval(phoneSelector, p => p.innerText);
      const phone = formatPhoneNumber(phoneNumberRaw);
      const latitude = await page.$eval(latitudeSelector, e => e.getAttribute('content'));
      const longitude = await page.$eval(longitudeSelector, e => e.getAttribute('content'));
      const hoursRaw = await page.$eval(hourSelector, h => h.innerText);
      const hours_of_operation = formatHours(hoursRaw);

      const poiData = {
        locator_domain: 'tuesdaymorning.com',
        location_name,
        street_address,
        city,
        state,
        zip,
        country_code,
        phone,
        store_number,
        latitude,
        longitude,
        hours_of_operation,
      };

      const poi = new Poi(poiData);
      await Apify.pushData(poi);
      await page.waitFor(2000);
    },
  });

  await crawler.run();
});
