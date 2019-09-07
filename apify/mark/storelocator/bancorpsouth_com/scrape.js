const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');
const _ = require('underscore');
const {
  formatPhoneNumber,
  parseGoogleMapsUrl,
  formatStreetAddress,
  parseAddress,
  checkLocationType,
} = require('./tools');
const {
  Poi,
} = require('./Poi');

const { log } = Apify.utils;
const bancorpSitemap = 'https://www.bancorpsouth.com/sitemap.xml';

Apify.main(async () => {
  // Get list of urls from store locator sitemap
  const xml = await rp(bancorpSitemap);
  const $c = cheerio.load(xml);
  const allurls = $c('loc').map((i, e) => ({ url: $c(e).text() })).toArray();
  const urls = allurls.filter(v => v.url.includes('find-a-location/'));

  const requestList = new Apify.RequestList({
    sources: urls,
  });
  await requestList.initialize();

  /* eslint-disable no-unused-vars */
  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ request, page }) => {
      const storeElement = 'body > section > div > div > div > div:nth-child(2) > h1';
      await page.waitForSelector(storeElement);
      const locationName = await page.$eval(storeElement, e => e.innerText);

      const leftBlock = 'body > section > div > div > div > div.row-fluid.branch-info > div:nth-child(1)';
      await page.waitForSelector(leftBlock);
      const infoBlockLeft = await page.$eval(leftBlock, e => e.innerHTML);
      const infoBlockLeftClean = infoBlockLeft.split('<br>').map(e => e.trim());
      const cityStateZipObj = parseAddress(infoBlockLeftClean[2]);

      const rightBlock = 'body > section > div > div > div > div.row-fluid.branch-info > div:nth-child(2)';
      await page.waitForSelector(rightBlock);
      const infoBlockRight = await page.$eval(rightBlock, e => e.innerHTML);
      const infoBlockRightClean = infoBlockRight.split('<br>').map(e => e.trim()).filter(e => e.length !== 0).join(' ')
        .replace(/&nbsp;/g, '');

      await page.waitForSelector('#google-map > div > div > div:nth-child(3) > a');
      const googleMapsUrl = await page.$eval('#google-map > div > div > div:nth-child(3) > a', e => e.getAttribute('href'));
      const coordinates = parseGoogleMapsUrl(googleMapsUrl);

      const poiData = {
        locator_domain: 'bancorpsouth.com',
        location_name: locationName,
        street_address: formatStreetAddress(infoBlockLeftClean[0], infoBlockLeftClean[1]),
        ...cityStateZipObj,
        country_code: undefined,
        phone: formatPhoneNumber(infoBlockLeftClean[3]),
        location_type: checkLocationType(request.url),
        ...coordinates,
        hours_of_operation: infoBlockRightClean,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    },
    launchPuppeteerOptions: { headless: true },
    maxRequestsPerCrawl: 500,
    maxConcurrency: 10,
    maxRequestRetries: 1,
    handlePageTimeoutSecs: 60,
    handleFailedRequestFunction: ({ request }) => {
      const details = _.pick(request, 'id', 'url', 'method', 'uniqueKey');
      log.error('Bancorp Crawler: Request failed and reached maximum retries', { errorDetails: details });
    },
  });

  await crawler.run();
});
