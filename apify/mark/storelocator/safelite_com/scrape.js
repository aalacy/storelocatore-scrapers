const Apify = require('apify');
const axios = require('axios');
const parser = require('xml2json');
const {
  storeExistsSelector,
  addressExistsSelector,
  addressSelector,
  googleMapSelector,
  cityStateSelector,
  getPhoneSelector,
  getHoursSelector,
  getScheduleButtonSelector
} = require('./selectors');

const { MISSING, formatPhoneNumber, formatAddress, formatHours } = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const { data } = await axios.get('https://www.safelite.com/sitemap.xml');
  const sitemap = JSON.parse(parser.toJson(data));
  const urls = sitemap.urlset.url;

  const requestQueue = await Apify.openRequestQueue();
  const storeUrls = urls.filter((url) => url.loc.match(/safelite.com\/stores\//));
  const promises = storeUrls.map((store) => requestQueue.addRequest({ url: store.loc }));
  await Promise.all(promises);

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    launchPuppeteerOptions: {
      headless: true,
      useChrome: true,
      stealth: true,
      ignoreHTTPSErrors: true,
      args: ['--ignore-certificate-errors'],
    },
    maxRequestsPerCrawl: 20000,
    maxConcurrency: 10,
    handlePageFunction: async ({ request, page }) => {
      // Check if link redirects to store search page
      await page.waitFor(500);
      if (!(await page.$(storeExistsSelector))) return;

      const maybeAddress = await page.$(addressExistsSelector)
      const hasAddress = maybeAddress && (await page.$eval(addressExistsSelector, p => p.innerText)).match(/address/);
      const hasScheduleButton = await page.$(getScheduleButtonSelector(hasAddress));
      // Some stores have a location selector, but are mobile vans
      const addressRaw = hasAddress
          ? await page.$eval(addressSelector, (p) => p.innerText)
          : await page.$eval(cityStateSelector, (p) => p.innerText);

      const hoursRaw = await page.$eval(getHoursSelector(hasAddress, hasScheduleButton), (h) => h.innerText)
      const phoneNumberRaw = await page.$eval(getPhoneSelector(hasAddress), (p) => p.innerText);
      
      const address = formatAddress(addressRaw);
      const phone = formatPhoneNumber(phoneNumberRaw)
      const hours_of_operation = formatHours(hoursRaw);

      const latLon = hasAddress
      ? await page.$eval(googleMapSelector, (map) => ({
        latitude: map.getAttribute('data-start-lat'),
        longitude: map.getAttribute('data-start-lon')
      }))
      : {latitude: null, longitude: null }

      const poiData = {
        ...latLon,
        ...address,
        phone,
        hours_of_operation,
        locator_domain: 'safelite.com',
        location_name: MISSING,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
  });

  await crawler.run();
});
