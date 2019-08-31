const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');

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
  formatHours,
  formatPhoneNumber,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  // Cheerio crawler is unable to load .xml sites, so we preload the site.
  const siteMapUrl = 'https://www.smartstyle.com/content/dam/sitemaps/smartstyle/sitemap_smartstyle_en_us.xml';
  const xml = await rp(siteMapUrl);
  const $c = cheerio.load(xml);
  const urls = $c('loc').map((i, e) => ({ url: $c(e).text() })).toArray();

  const locationUrls = urls.filter(e => e.url.match(/www.smartstyle.com\/en-us\/locations\/[a-z][a-z]\/.*\//));

  const requestList = new Apify.RequestList({
    sources: locationUrls,
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({
      $,
    }) => {
      /* eslint-disable camelcase */
      const location_name = $(locationNameSelector).text();
      const street_address = $(streetAddressSelector).text();
      const city = $(citySelector).text();
      const state = $(stateSelector).text();
      const zip = $(zipSelector).text();
      const phone = $(phoneSelector).text();
      const latitude = $(latitudeSelector).attr('content');
      const longitude = $(longitudeSelector).attr('content');
      const hours = $(hourSelector).text();

      const poiData = {
        locator_domain: 'smartstyle.com',
        location_name,
        street_address,
        city,
        state,
        zip,
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
