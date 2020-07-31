const Apify = require('apify');
const randomUA = require('modern-random-ua');

const MISSING_DATA = '<MISSING>';
const BASE_URL = 'https://www.wawa.com';
const SITEMAP = 'site-map';

async function handlePageFunction(requestQueue, { request, page }) {
  switch (request.userData.pageType) {
    case 'stores':
      await getStores({ page, requestQueue });
      break;

    case 'storeDetails':
      await getStoreDetails({ page, request });
      break;
  }
}

async function getStores({ page, requestQueue }) {
  // find links to store details
  await Apify.utils.enqueueLinks({
    page,
    requestQueue,
    selector: 'a.CMSSiteMapLink',
    pseudoUrls: [`${BASE_URL}/stores/[.*]`],
    transformRequestFunction(request) {
      request.userData.pageType = 'storeDetails';
      return request;
    },
  });
}

async function getStoreDetails({ page }) {
  const info = await getBasicInfo(page);
  const location = await getGeolocation(page);

  const poi = {
    location_domain: BASE_URL,
    page_url: page.url(),
    location_name: info.name,
    store_number: info.storeNumber,
    hours_of_operation: info.hours,
    street_address: location.street,
    city: location.city,
    state: location.state,
    zip: location.zip,
    country_code: location.countryCode,
    phone: info.phoneNumber,
    location_type: location.type,
    latitude: location.latitude,
    longitude: location.longitude,
  };

  await Apify.pushData([poi]);
}

async function getBasicInfo(page) {
  const name = await page.$('span[itemprop="name"]');
  console.log(name.jsonValue());
  return {
    name,
    // storeNumber,
    // phoneNumber,
    // hours,
  };
}

async function getGeolocation(page) {
  return {
    // street,
    // city,
    // zip,
    // countryCode,
    // type,
    // latitude,
    // longitude,
  };
}

Apify.main(async () => {
  const url = `${BASE_URL}/${SITEMAP}`;
  const requestQueue = await Apify.openRequestQueue();
  requestQueue.addRequest({
    url,
    userData: {
      pageType: 'stores',
    },
  });

  const useProxy = process.env.USE_PROXY;
  const proxyConfiguration = await Apify.createProxyConfiguration({
    groups: ['RESIDENTIAL'], // List of Apify Proxy groups
    countryCode: 'US',
  });

  // Getting proxyInfo object by calling class method directly
  const proxyInfo = proxyConfiguration.newProxyInfo();

  const puppeteerPoolOptions = {
    retireInstanceAfterRequestCount: 1,
  };

  const launchPuppeteerOptions = {
    headless: false,
    stealth: true,
    useChrome: true,
    useApifyProxy: !!useProxy,
    userAgent: randomUA.generate(),
    ignoreHTTPSErrors: true,
  };

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: handlePageFunction.bind(this, requestQueue),
    puppeteerPoolOptions,
    launchPuppeteerOptions,
    proxyConfiguration,
    maxConcurrency: 1,
    maxRequestsPerCrawl: 1,
  });

  await crawler.run();
});
