const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');

const {
  streetAddressSelector,
  streetAddress2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hoursSelector,
} = require('./selectors');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteMapUrl = 'https://locations.mamafus.com/sitemap.xml';

  const xml = await rp.get(siteMapUrl);
  const $c = cheerio.load(xml);
  const urls = $c('loc').map((i, e) => ({ url: $c(e).text() })).toArray();
  const adjustedUrls = urls.filter(e => e.url.match(/locations.mamafus.com\/(\w|-)+\/(\w|-)+\/(\w|-)+.html$/));

  const requestList = new Apify.RequestList({
    sources: adjustedUrls,
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ $ }) => {
      /* eslint-disable camelcase */
      let street_address;
      const streetAddress1 = $(streetAddressSelector).first().text();
      const streetAddress2 = $(streetAddress2Selector).first().text();
      if (streetAddress2) {
        street_address = `${streetAddress1}, ${streetAddress2}`;
      } else {
        street_address = `${streetAddress1}`;
      }
      const city = $(citySelector).text();
      const state = $(stateSelector).text();
      const zip = $(zipSelector).text();
      const phone = $(phoneSelector).first().text();
      const latitude = $(latitudeSelector).attr('content');
      const longitude = $(longitudeSelector).attr('content');
      const hoursRaw = $(hoursSelector).first().text();

      const poiData = {
        locator_domain: 'mamafus_com',
        street_address,
        city,
        state,
        zip,
        phone,
        latitude,
        longitude,
        hours_of_operation: hoursRaw,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
    maxRequestsPerCrawl: 30,
    maxConcurrency: 10,
  });

  await crawler.run();
});
