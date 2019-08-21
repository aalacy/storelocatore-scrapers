const Apify = require('apify');

const {
  locationExistsSelector,
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  geoUrlSelector,
} = require('./selectors');

const {
  formatAddress,
  parseGoogleMapsUrl,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const siteMapUrl = 'https://www.mrhandyman.com/sitemap.xml';

  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto(siteMapUrl, {
    timeout: 0, waitUntil: 'load',
  });

  const allUrls = await p.$$eval('span', ae => ae.map(a => a.innerText));
  const locationUrls = allUrls.filter(e => e !== null).filter(e => e.match(/www.mrhandyman.com\/(\w|-)+\/$/));
  const adjustedUrls = locationUrls.map(e => ({ url: `${e.trim()}` }));
  await browser.close();

  const requestList = new Apify.RequestList({
    sources: adjustedUrls,
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ $ }) => {
      /* eslint-disable camelcase */
      const locationExists = $(locationExistsSelector).attr('content');
      if (locationExists) {
        const location_name = $(locationNameSelector).attr('content');
        const streetAddressRaw = $(streetAddressSelector).text();
        const street_address = formatAddress(streetAddressRaw);
        const city = $(citySelector).text();
        const state = $(stateSelector).text();
        const zip = $(zipSelector).text();
        const phone = $(phoneSelector).first().text();
        let latitude = $(latitudeSelector).attr('content');
        let longitude = $(longitudeSelector).attr('content');

        if (latitude && latitude.length < 6) {
          const geoUrl = $(geoUrlSelector).attr('href');
          const geoObject = parseGoogleMapsUrl(geoUrl);
          ({ latitude, longitude } = geoObject);
        }
        const poiData = {
          locator_domain: 'mrhandyman_com',
          location_name,
          street_address,
          city,
          state,
          zip,
          phone,
          latitude,
          longitude,
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();
});
