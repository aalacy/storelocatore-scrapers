const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');
const _ = require('underscore');
const {
  formatPhoneNumber,
  extractHourString,
} = require('./tools');

const { Poi } = require('./Poi');

const { log } = Apify.utils;
const verizonurl = 'https://www.verizonwireless.com/sitemap_storelocator.xml?intcmp=vzwdom';

// $c is cheerio but to avoid conflict with the crawler.
Apify.main(async () => {
  // Get list of urls from store locator sitemap
  const xml = await rp(verizonurl);
  const $c = cheerio.load(xml);
  const urls = $c('loc').map((i, e) => ({ url: $c(e).text() })).toArray();

  const requestList = new Apify.RequestList({
    sources: urls,
  });
  await requestList.initialize();

  /* eslint-disable no-unused-vars */
  const crawler = new Apify.CheerioCrawler({
    requestList,
    minConcurrency: 1,
    maxConcurrency: 10,
    maxRequestRetries: 2,
    handlePageTimeoutSecs: 60,
    handleFailedRequestFunction: ({ request }) => {
      const details = _.pick(request, 'id', 'url', 'method', 'uniqueKey');
      log.error('Verizon Crawler: Request failed and reached maximum retries', { errorDetails: details });
    },
    handlePageFunction: async ({
      request, response, html, $,
    }) => {
      const pageTitle = $('#pageTitle > h1').text();
      // Only push data for pages Verizon has
      if (pageTitle !== 'Page is not currently available') {
        const dataSubset = $('#storeLocator > script:nth-child(10)').html();
        const locationObject = JSON.parse(dataSubset);
        const storeName = $('#storeLocator > div > div > div.store-info-details > h1').text();

        const poiData = {
          locator_domain: 'verizonwireless.com',
          location_name: storeName,
          street_address: locationObject.address.streetAddress,
          city: locationObject.address.addressLocality,
          state: locationObject.address.addressRegion,
          zip: locationObject.address.postalCode,
          country_code: locationObject.address.addressCountry,
          store_number: undefined,
          phone: formatPhoneNumber(locationObject.telephone),
          latitude: locationObject.geo.latitude,
          longitude: locationObject.geo.longitude,
          hours_of_operation: extractHourString(locationObject.openingHoursSpecification[0].dayOfWeek),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();
});
