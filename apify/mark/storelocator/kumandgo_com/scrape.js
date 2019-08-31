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
  geoSelector,
  hourSelector,
} = require('./selectors');

const {
  formatHours,
  formatPhoneNumber,
  removeEmptyStringProperties,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  // Cheerio crawler is unable to load .xml sites, so we preload the site.
  const siteMapUrl = 'https://www.kumandgo.com/location-sitemap.xml';
  const xml = await rp(siteMapUrl);
  const $c = cheerio.load(xml);
  const urls = $c('loc').map((i, e) => ({ url: $c(e).text() })).toArray();

  const requestList = new Apify.RequestList({
    sources: urls,
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
      const store_number = $(geoSelector).attr('data-store-id');
      const latitude = $(geoSelector).attr('data-latitude');
      const longitude = $(geoSelector).attr('data-longitude');
      const hours = $(hourSelector).children().first().text();

      const poiData = {
        locator_domain: 'kumandgo.com',
        location_name,
        street_address,
        city,
        state,
        zip,
        country_code: undefined,
        store_number,
        phone: formatPhoneNumber(phone),
        latitude,
        longitude,
        hours_of_operation: formatHours(hours),
      };

      const cleanPoiData = removeEmptyStringProperties(poiData);
      const poi = new Poi(cleanPoiData);
      await Apify.pushData(poi);
    },
  });

  await crawler.run();
});
