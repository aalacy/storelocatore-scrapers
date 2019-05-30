const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');
const _ = require('underscore');
const { formatData } = require('./tools');

const { log } = Apify.utils;
const verizonurl = 'https://www.verizonwireless.com/sitemap_storelocator.xml?intcmp=vzwdom';

// $c is cheerio but to avoid conflict with the crawler.
Apify.main(async () => {
  // Get list of urls from store locator sitemap
  const xml = await rp(verizonurl);
  const $c = cheerio.load(xml);
  const urls = $c('loc')
    .map((i, e) => ({ url: $c(e).text() }))
    .toArray();

  const requestList = new Apify.RequestList({
    sources: urls,
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    minConcurrency: 1,
    maxConcurrency: 5,
    maxRequestRetries: 3,
    handlePageTimeoutSecs: 60,
    handleFailedRequestFunction: ({ request }) => {
      const details = _.pick(request, 'id', 'url', 'method', 'uniqueKey');
      log.error('Verizon Crawler: Request failed and reached maximum retries', {
        errorDetails: details,
      });
    },
    handlePageFunction: async ({ request, response, html, $ }) => {
      const pageTitle = $('#pageTitle > h1').text();
      // Only push data for pages Verizon has
      if (pageTitle !== 'Page is not currently available') {
        const dataSubset = $('#storeLocator > script:nth-child(10)').html();
        const dataSubsetObject = JSON.parse(dataSubset);
        const storeName = $('#storeLocator > div > div > div.store-info-details > h1').text();
        const preFormatData = { location_name: storeName, ...dataSubsetObject };
        Apify.pushData(formatData(preFormatData));
      }
    },
  });

  await crawler.run();
});
