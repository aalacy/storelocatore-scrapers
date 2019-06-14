const Apify = require('apify');

const {
  locationNameSelector,
  checkAddressExists,
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
  formatPhoneNumber,
  formatHours,
  formatData,
} = require('./tools');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.signaturestyle.com/content/dam/sitemaps/signaturestyle/sitemap_signaturestyle_en_us.xml',
    userData: {
      urlType: 'initial',
    },
  });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
        const urls = await page.$$eval('span', se => se.map(s => s.innerText));
        const locationUrls = urls.filter(e => e.match(/https:\/\/www.signaturestyle.com\/locations\/[a-zA-Z][a-zA-Z]\/(\w|-)+\/cost-cutters-/))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        await page.waitFor(5000);
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
      if (request.userData.urlType === 'detail') {
        if (await page.$(checkAddressExists) !== null) {
          await page.waitForSelector(locationNameSelector, { waitUntil: 'load', timeout: 0 });
          /* eslint-disable camelcase */
          const location_name = await page.$eval(locationNameSelector, e => e.innerText);
          const street_address = await page.$eval(streetAddressSelector, e => e.innerHTML);
          const city = await page.$eval(citySelector, e => e.innerText);
          const state = await page.$eval(stateSelector, e => e.innerText);
          const zip = await page.$eval(zipSelector, e => e.innerText);
          const phoneNumberRaw = await page.$eval(phoneSelector, e => e.innerText);
          const phone = formatPhoneNumber(phoneNumberRaw);
          const latitude = await page.$eval(latitudeSelector, e => e.getAttribute('content'));
          const longitude = await page.$eval(longitudeSelector, e => e.getAttribute('content'));
          const hoursRaw = await page.$eval(hourSelector, e => e.innerText);
          const hours_of_operation = formatHours(hoursRaw);

          const poi = {
            locator_domain: 'signaturestyle.com',
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code: 'US',
            phone,
            location_type: 'Salon',
            latitude,
            longitude,
            hours_of_operation,
          };
          await Apify.pushData(formatData(poi));
          await page.waitFor(5000);
        } else {
          await page.waitFor(5000);
          if (await requestQueue.isEmpty()) {
            await requestQueue.fetchNextRequest();
          }
        }
      }
    },
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 4,
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
      timeout: 0, waitUntil: 'load',
    }),
  });

  await crawler.run();
});
