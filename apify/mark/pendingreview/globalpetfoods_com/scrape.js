const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');

const {
  locationNameSelector,
  streetAddressSelector,
  addressLine2Selector,
  phoneSelector,
  hourSelector,
} = require('./selectors');

const {
  extractLocationInfo,
  formatPhoneNumber,
  formatHours,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

const locationSitemap = 'https://globalpetfoods.com/portal/store-locations-sitemap/';

Apify.main(async () => {
  // Get list of urls from store locator sitemap
  const xml = await rp(locationSitemap);
  const $c = cheerio.load(xml);
  const allurls = $c('loc').map((i, e) => ({ url: $c(e).text() })).toArray();
  const urls = allurls.filter(e => e.url.match(/globalpetfoods.com\/store-locations\/s\//));

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
      const streetAddress = $(streetAddressSelector).text();
      const addressLine2 = $(addressLine2Selector).text();
      const phoneRaw = $(phoneSelector).text();
      const hours = $(hourSelector).text();
      const addressData = extractLocationInfo(streetAddress, addressLine2);
      const poiData = {
        locator_domain: 'globalpetfoods.com',
        location_name,
        ...addressData,
        phone: formatPhoneNumber(phoneRaw),
        hours_of_operation: formatHours(hours),
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
    minConcurrency: 5,
    maxConcurrency: 20,
    maxRequestRetries: 1,
    handlePageTimeoutSecs: 60,
  });

  await crawler.run();
});
