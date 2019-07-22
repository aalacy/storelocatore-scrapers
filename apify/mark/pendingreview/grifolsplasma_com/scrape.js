const Apify = require('apify');

const {
  locationHrefSelector,
  locationNameSelector,
  streetAddressSelector,
  cityStateZipSelector,
  phoneSelector,
  geoUrlSelector,
  hourSelector,
} = require('./selectors');

const {
  extractLocationInfo,
  parseGoogleMapsUrl,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const initialUrl = 'https://www.grifolsplasma.com/en/locations/find-a-donation-center';
  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(initialUrl, { waitUntil: 'networkidle0', timeout: 30000 });
  const locationLinks = await p.$$eval(locationHrefSelector, se => se.map(s => s.getAttribute('href')));
  const allRequests = locationLinks.map(e => ({ url: e }));

  console.log(allRequests.length);

  const requestList = new Apify.RequestList({
    sources: allRequests,
  });
  await requestList.initialize();
  await browser.close();

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({
      page,
    }) => {
      /* eslint-disable camelcase */
      const location_name = await page.$eval(locationNameSelector, e => e.innerText);
      const streetAddress = await page.$eval(streetAddressSelector, e => e.innerText);
      const cityStateZip = await page.$eval(cityStateZipSelector, e => e.innerText);
      const phone = await page.$eval(phoneSelector, e => e.innerText);
      const googleMapsUrl = await page.$eval(geoUrlSelector, e => e.getAttribute('href'));
      const hoursArrayRaw = await page.$$eval(hourSelector, se => se.map(e => e.innerText));
      const hoursArrayClean = hoursArrayRaw.map(e => e.replace(/\n/g, '').replace(/\t/g, ''));
      const hours_of_operation = hoursArrayClean.join(', ');
      const addressInfo = extractLocationInfo(streetAddress, cityStateZip);
      const latLong = parseGoogleMapsUrl(googleMapsUrl);
      const poiData = {
        locator_domain: 'greenmill.com',
        location_name,
        ...addressInfo,
        phone,
        ...latLong,
        hours_of_operation,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
    maxRequestsPerCrawl: 230,
    maxConcurrency: 10,
    launchPuppeteerOptions: {
      headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy,
    },
    gotoFunction: async ({
      request, page,
    }) => {
      await page.goto(request.url, {
        timeout: 60000, waitUntil: 'load',
      });
    },
  });

  await crawler.run();
});
