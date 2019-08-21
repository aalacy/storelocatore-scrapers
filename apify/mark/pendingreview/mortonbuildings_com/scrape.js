const Apify = require('apify');

const {
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
} = require('./selectors');

const {
  removeSpaces,
  formatGeo,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteMapUrl = 'https://mortonbuildings.com/sitemaps-1-section-location-1-sitemap.xml';

  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(siteMapUrl, {
    timeout: 0, waitUntil: 'load',
  });

  const allUrls = await p.$$eval('span', ae => ae.map(a => a.innerText));
  const locationUrls = allUrls.filter(e => e !== null).filter(e => e.match(/mortonbuildings.com\/location\/(\w|-)+/));
  const adjustedUrls = locationUrls.map(e => ({ url: `${e.trim()}` }));
  await browser.close();

  const requestList = new Apify.RequestList({
    sources: adjustedUrls,
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ $ }) => {
      /* eslint-disable camelcase */
      const streetAddressRaw = $(streetAddressSelector).first().text();
      const street_address = removeSpaces(streetAddressRaw);
      const cityRaw = $(citySelector).first().text();
      const city = removeSpaces(cityRaw);
      const stateRaw = $(stateSelector).first().text();
      const state = removeSpaces(stateRaw);
      const zipRaw = $(zipSelector).first().text();
      const zip = removeSpaces(zipRaw);
      const phoneRaw = $(phoneSelector).text();
      const phone = removeSpaces(phoneRaw);
      /* eslint-disable func-names */
      const allHrefs = $('a').map(function () {
        return $(this).attr('href');
      }).get();
      const [geoHref] = allHrefs.filter(e => e.includes('www.google.com/maps/dir/?api'));
      const latLong = formatGeo(geoHref);

      const poiData = {
        locator_domain: 'mortonbuildings_com',
        street_address,
        city,
        state,
        zip,
        phone,
        ...latLong,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
  });

  await crawler.run();
});
