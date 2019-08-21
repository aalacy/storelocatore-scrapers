const Apify = require('apify');

const {
  dropdownHrefSelector,
  locationBlockSelector,
  locationNameSelector,
  addressPhoneBlockSelector,
} = require('./selectors');

const {
  parseAddress,
  parseGoogleMapsUrl,
  formatAddressLine2,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteUrl = 'https://www.greencactusgrill.com';
  const baseUrl = 'https://www.greencactusgrill.com';

  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(siteUrl, {
    timeout: 0, waitUntil: 'load',
  });
  const allUrls = await p.$$eval(dropdownHrefSelector, ae => ae.map(a => a.getAttribute('href')));
  const uniqueUrls = Array.from(new Set(allUrls));
  const adjustedUrls = uniqueUrls.map(e => ({ url: `${baseUrl}${e}` }));
  await browser.close();

  const requestList = new Apify.RequestList({
    sources: adjustedUrls,
  });
  await requestList.initialize();

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ page }) => {
      /* eslint-disable camelcase */
      let street_address;
      let city;
      let state;
      let zip;
      let phone;
      const addressBlockElement = await page.$(locationBlockSelector);
      const location_name = await addressBlockElement.$eval(locationNameSelector, s => s.innerText);

      // One site currently has a different format than the others. This is a temporary fix,
      // but eventually the latter else statement should be the finished solution.

      if (await addressBlockElement.$('p:nth-child(3)')) {
        const streetAddressRaw = await addressBlockElement.$eval('p:nth-child(2)', e => e.innerText);
        street_address = streetAddressRaw.trim();
        const cityStateZip = await addressBlockElement.$eval('p:nth-child(3)', e => e.innerText);
        ({ city, state, zip } = formatAddressLine2(cityStateZip));
        phone = await addressBlockElement.$eval('p:nth-child(4)', e => e.innerText);
      } else {
        const addressPhoneBlockRaw = await addressBlockElement
          .$eval(addressPhoneBlockSelector, s => s.innerText);
        ({
          street_address, city, state, zip, phone,
        } = parseAddress(addressPhoneBlockRaw));
      }
      await page.waitFor(5000);
      await page.waitForSelector('div > div > div > div:nth-child(3) > a', { waitUntil: 'networkidle0', timeout: 0 });
      const geoUrl = await page.$eval('div > div > div > div:nth-child(3) > a', e => e.getAttribute('href'));
      const { latitude, longitude } = parseGoogleMapsUrl(geoUrl);

      const poiData = {
        locator_domain: 'greencactusgrill_com',
        location_name,
        street_address,
        city,
        state,
        zip,
        phone,
        latitude,
        longitude,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
    maxRequestsPerCrawl: 10,
    maxConcurrency: 4,
    launchPuppeteerOptions: {
    // In order to function properly, it needs a larger window size to load the map
      defaultViewport: null,
      headless: true,
      stealth: true,
      useChrome: true,
      useApifyProxy: !!useProxy,
      args: ['--window-size=1920,1080'],
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
