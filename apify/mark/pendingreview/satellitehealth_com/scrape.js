const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');

const {
  locationInfoSelector,
  hourSelector,
} = require('./selectors');

const {
  upperCaseWords,
  formatHours,
  storeKey,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

const locationSitemap = 'http://www.satellitehealth.com/SiteMap.xml';

Apify.main(async () => {
  // Open a store to remove duplicates
  const dataStorage = await Apify.openKeyValueStore('poidata');
  const xml = await rp(locationSitemap);
  const $c = cheerio.load(xml);
  const allurls = $c('loc').map((i, e) => ({ url: $c(e).text() })).toArray();
  const urls = allurls
    .filter(e => e.url.match(/www.satellitehealth.com\/satellite-healthcare-(\w|-)+\/$/) || e.url.match(/www.satellitehealth.com\/wellbound-(\w|-)+\/$/));

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
      const location_name = $(locationInfoSelector).attr('data-name');
      const street_address = $(locationInfoSelector).attr('data-address');
      const city = $(locationInfoSelector).attr('data-city');
      const state = $(locationInfoSelector).attr('data-state');
      const zip = $(locationInfoSelector).attr('data-zip');
      const phone = $(locationInfoSelector).attr('data-phone');
      const latitude = $(locationInfoSelector).attr('data-latitude');
      const longitude = $(locationInfoSelector).attr('data-longitude');
      const hours = $(hourSelector).text();

      const poiData = {
        locator_domain: 'satellitehealth.com',
        location_name: upperCaseWords(location_name),
        street_address: upperCaseWords(street_address),
        city: upperCaseWords(city),
        state: state.toUpperCase(),
        zip,
        phone,
        latitude,
        longitude,
        hours_of_operation: formatHours(hours),
      };

      const key = storeKey(poiData.latitude);
      await dataStorage.setValue(key, poiData);
    },
    minConcurrency: 5,
    maxConcurrency: 20,
    maxRequestRetries: 1,
    handlePageTimeoutSecs: 60,
  });

  await crawler.run();
  if (requestList.isFinished()) {
    await dataStorage.forEachKey(async (key) => {
      if (key) {
        const storeInfo = await dataStorage.getValue(key);
        const poi = new Poi(storeInfo);
        await Apify.pushData(poi);
      }
    });
  }
});
