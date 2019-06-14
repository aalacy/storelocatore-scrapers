const Apify = require('apify');

const {
  locationNameSelector,
  checkAddressExists,
  streetAddressSelector,
  streetAddress2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  mapButtonSelector,
  linkSelector,
  hourSelector,
} = require('./selectors');

const {
  formatPhoneNumber,
  formatHours,
  parseGoogleMapsUrl,
  formatData,
} = require('./tools');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://nortonhealthcare.com/sitemap-xml-location',
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
        const locationUrls = urls.filter(e => e.match(/https:\/\/nortonhealthcare.com\/location\//))
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
          let street_address;
          // Some addresses have two lines for the address
          if (await page.$(streetAddress2Selector) !== null) {
            const street1 = await page.$eval(streetAddressSelector, e => e.innerText);
            await page.waitForSelector(streetAddress2Selector);
            const street2 = await page.$eval(streetAddress2Selector, e => e.innerText);
            street_address = `${street1}, ${street2}`;
          }
          if (await page.$(streetAddress2Selector) === null) {
            street_address = await page.$eval(streetAddressSelector, e => e.innerText);
          }
          const city = await page.$eval(citySelector, e => e.innerText);
          const state = await page.$eval(stateSelector, e => e.innerText);
          const zip = await page.$eval(zipSelector, e => e.innerText);
          const phoneNumberRaw = await page.$eval(phoneSelector, e => e.innerText);
          const phone = formatPhoneNumber(phoneNumberRaw);
          await page.click(mapButtonSelector);
          await page.waitForSelector(linkSelector, { waitUntil: 'networkidle0', timeout: 0 });
          const allHrefs = await page.$$eval('a', ae => ae.map(a => a.href));
          let latLong;
          const urlArray = allHrefs.filter(e => e.includes('https://maps.google.com/maps?ll='));
          if (urlArray !== undefined || urlArray.length !== 0) {
            const googleMapsUrl = urlArray[0];
            latLong = parseGoogleMapsUrl(googleMapsUrl);
          }
          const hoursRaw = await page.$eval(hourSelector, e => e.innerText);
          const hours_of_operation = formatHours(hoursRaw);

          const poi = {
            locator_domain: 'nortonhealthcare.com',
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code: 'US',
            phone,
            ...latLong,
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
    maxConcurrency: 1,
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
      timeout: 0, waitUntil: 'load',
    }),
  });

  await crawler.run();
});
