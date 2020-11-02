const Apify = require('apify');

const {
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

const { Poi } = require('./Poi');

Apify.main(async () => {
  // Cheerio crawler is unable to load .xml sites, so we preload the site.
  const siteMapUrl = 'https://www.dippindots.com/loc/site-map/US';

  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(siteMapUrl, {
    timeout: 0, waitUntil: 'load',
  });

  const allUrls = await p.$$eval('a', ae => ae.map(a => a.getAttribute('href')));
  const locationUrls = allUrls.filter(e => e !== null).filter(e => e.match(/\/ll\/US\/[A-Z][A-Z]\/.*\/.*/));
  const baseUrl = 'https://www.dippindots.com/loc';
  const adjustedUrls = locationUrls.map(e => ({ url: `${baseUrl}${e}` }));


  await browser.close();

  const requestList = new Apify.RequestList({
    sources: adjustedUrls,
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
    maxRequestsPerCrawl: 300,
    minimumConcurrency: 4,
    maxConcurrency: 10,
    handlePageFunction: async ({
      page,
    }) => {
      /* eslint-disable camelcase */
      const street_address = await page.$eval(streetAddressSelector, e => e.innerText);
      const city = await page.$eval(citySelector, e => e.innerText);
      const state = await page.$eval(stateSelector, e => e.innerText);
      const zip = await page.$eval(zipSelector, e => e.innerText);
      const phone = await page.$eval(phoneSelector, e => e.innerText);
      const latitude = await page.$eval(latitudeSelector, e => e.getAttribute('content'));
      const longitude = await page.$eval(longitudeSelector, e => e.getAttribute('content'));
      const hours = await page.$eval(hourSelector, e => e.getAttribute('content'));

      const poiData = {
        locator_domain: 'dippindots.com',
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
