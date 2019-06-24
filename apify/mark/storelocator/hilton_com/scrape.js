const Apify = require('apify');

const {
  formatLocationObject,
  formatObject,
  formatPhoneNumber,
  formatData,
} = require('./tools');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www3.hilton.com/sitemapurl-hi-00000.xml',
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
        const locationUrls = urls.filter(e => e.match(/www3.hilton.com\/en\/hotels\/(\w|-)+\/(\w|-)+\/index.html/))
          .map(e => ({ url: e, userData: { urlType: 'detail' } }));
        /* eslint-disable no-restricted-syntax */
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
        await page.waitFor(5000);
      }
      if (request.userData.urlType === 'detail') {
        const allScripts = await page.$$eval('script', se => se.map(s => s.innerText));
        const locationObjectArray = allScripts.filter(e => e.includes('latitude'));
        const locationObjectRaw = locationObjectArray[0];
        const locationObject = formatLocationObject(locationObjectRaw);
        const additionalInfoArray = allScripts.filter(e => e.includes('propertySearchCountry'));
        const additionalInfoString = additionalInfoArray[0];
        const additionalInfoRaw = additionalInfoString.substring(additionalInfoString.indexOf('{'), additionalInfoString.indexOf(']}') + 2);
        const additionalInfoObject = formatObject(additionalInfoRaw);

        const poi = {
          locator_domain: 'hilton.com',
          location_name: locationObject.name,
          street_address: locationObject.address.streetAddress,
          city: locationObject.address.addressLocality,
          state: locationObject.address.addressRegion,
          zip: locationObject.address.postalCode,
          country_code: additionalInfoObject.page.attributes.propertySearchCountry,
          store_number: undefined,
          phone: formatPhoneNumber(locationObject.telephone),
          location_type: additionalInfoObject.page.category.brand,
          naics_code: undefined,
          latitude: locationObject.geo.latitude,
          longitude: locationObject.geo.longitude,
          hours_of_operation: undefined,
        };
        await Apify.pushData(formatData(poi));
        await page.waitFor(5000);
      }
    },
    maxRequestsPerCrawl: 1000,
    maxConcurrency: 10,
    gotoFunction: async ({
      request, page,
    }) => {
      await Apify.utils.puppeteer.hideWebDriver(page);
      await page.goto(request.url, {
        timeout: 0, waitUntil: 'load',
      });
    },
  });

  await crawler.run();
});
