const Apify = require('apify');

const {
  locationNameSelector,
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
  formatAddress,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteMapUrl = 'https://www.monicals.com/locations/';

  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(siteMapUrl, {
    timeout: 0, waitUntil: 'load',
  });

  const allUrls = await p.$$eval('a', ae => ae.map(a => a.getAttribute('href')));
  const locationUrls = allUrls.filter(e => e !== null).filter(e => e.match(/locations\/monicals-(\w|-)+\//));
  const adjustedUrls = locationUrls.map(e => ({ url: `${e}` }));
  await browser.close();

  const requestList = new Apify.RequestList({
    sources: adjustedUrls,
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ $ }) => {
      /* eslint-disable camelcase */
      const location_name = $(locationNameSelector).text();
      const streetAddressRaw = $(streetAddressSelector).text();
      const street_address = formatAddress(streetAddressRaw);
      const city = $(citySelector).text();
      const state = $(stateSelector).text();
      const zip = $(zipSelector).text();
      const phone = $(phoneSelector).text();
      const latitude = $(latitudeSelector).attr('value');
      const longitude = $(longitudeSelector).attr('value');
      const hoursRaw = $(hourSelector).text();
      const hours_of_operation = formatHours(hoursRaw);

      const poiData = {
        locator_domain: 'monicals_com',
        location_name,
        street_address,
        city,
        state,
        zip,
        phone,
        latitude,
        longitude,
        hours_of_operation,
      };

      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
  });

  await crawler.run();
});
