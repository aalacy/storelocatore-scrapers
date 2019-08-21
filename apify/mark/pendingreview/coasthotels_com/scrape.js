const Apify = require('apify');

const {
  locationNameSelector,
  streetAddressSelector,
  addressBlockSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
} = require('./selectors');

const { parseAddress, cleanState } = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteUrl = 'https://www.coasthotels.com/hotels/';

  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(siteUrl, {
    timeout: 0, waitUntil: 'load',
  });
  const allUrls = await p.$$eval('div.desktop > section > a.btn', ae => ae.map(a => a.getAttribute('href')));
  const locationUrls = allUrls.filter(e => e !== null)
    .filter(e => e.match(/coasthotels.com\/hotels\/(\w|-)+\/(\w|-)+\/(\w|-)+\//));
  const adjustedUrls = locationUrls.map(e => ({ url: `${e}` }));
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
      const location_name = await page.$eval(locationNameSelector, e => e.innerText);

      // Currently one page does not have the typical format, you can remove this if statement and
      // the block below once the site fixes it.
      if (await page.$(streetAddressSelector) !== null) {
        const street_address = await page.$eval(streetAddressSelector, e => e.innerText);
        const city = await page.$eval(citySelector, e => e.innerText);
        const stateRaw = await page.$eval(stateSelector, e => e.innerText);
        const state = cleanState(stateRaw);
        const zip = await page.$eval(zipSelector, e => e.innerText);
        const phone = await page.$eval(phoneSelector, e => e.innerText);
        const poiData = {
          locator_domain: 'coasthotels_com',
          location_name,
          street_address,
          city,
          state,
          zip,
          phone,
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      } else if (await page.$(addressBlockSelector)) {
        const addressBlockRaw = await page.$eval(addressBlockSelector, e => e.innerText);
        const {
          street_address, city, state, zip, phone,
        } = parseAddress(addressBlockRaw);

        const poiData = {
          locator_domain: 'coasthotels_com',
          location_name,
          street_address,
          city,
          state,
          zip,
          phone,
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
    maxRequestsPerCrawl: 100,
    maxConcurrency: 10,
    launchPuppeteerOptions: {
      headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy,
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
