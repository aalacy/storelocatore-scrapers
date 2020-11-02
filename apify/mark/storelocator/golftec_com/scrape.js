const Apify = require('apify');
const cheerio = require('cheerio');
const rp = require('request-promise-native');

const {
  formatObject,
  formatCountry,
  formatHours,
  storeKey,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

const locationSitemap = 'https://www.golftec.com/sitemap-main.xml';

Apify.main(async () => {
  // Opening a key value store until end before we format results
  const dataStorage = await Apify.openKeyValueStore('poidata');
  // Get list of urls from store locator sitemap
  const requestQueue = await Apify.openRequestQueue();
  const xml = await rp(locationSitemap);
  const $c = cheerio.load(xml);
  const allurls = $c('loc').map((i, e) => ({ url: $c(e).text() })).toArray();
  const urls = allurls.filter(e => e.url.match(/www.golftec.com\/golf-lessons\//))
    .map(e => ({ url: e.url }));
  console.log(urls);
  /*
  const requestList = new Apify.RequestList({
    sources: urls,
  });
  await requestList.initialize();
  */
  /* eslint-disable no-restricted-syntax */
  for await (const url of urls) {
    await requestQueue.addRequest(url);
  }

  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({
      page,
    }) => {
      if (await page.$('body > div > div > article > div > div.center-details__text-wrap > div') !== null) {
        const allScripts = await page.$$eval('script', se => se.map(s => s.innerText));
        const locationScript = allScripts.filter(e => e.includes('streetAddress'));
        const locationObjectRaw = locationScript[0];
        const locationObject = formatObject(locationObjectRaw);
        /* eslint-disable camelcase */
        const poiData = {
          locator_domain: 'golftec.com',
          location_name: locationObject.name,
          street_address: locationObject.address.streetAddress,
          city: locationObject.address.addressLocality,
          state: locationObject.address.addressRegion,
          zip: locationObject.address.postalCode,
          country_code: formatCountry(locationObject.address.addressCountry),
          phone: locationObject.telephone,
          latitude: locationObject.geo.latitude,
          longitude: locationObject.geo.longitude,
          hours_of_operation: formatHours(locationObject.openingHoursSpecification),
        };
        const key = storeKey(poiData.street_address);
        await dataStorage.setValue(key, poiData);
      }
    },
    maxRequestsPerCrawl: 273,
    maxConcurrency: 10,
    maxRequestRetries: 1,
    launchPuppeteerOptions: {
      headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy,
    },
    gotoFunction: async ({
      request, page,
    }) => {
      await page.goto(request.url, {
        timeout: 60000, waitUntil: 'load',
      });
    },
  });

  await crawler.run();
  if (requestQueue.isFinished()) {
    await dataStorage.forEachKey(async (key) => {
      if (key) {
        const storeInfo = await dataStorage.getValue(key);
        const poi = new Poi(storeInfo);
        await Apify.pushData(poi);
      }
    });
  }
});
