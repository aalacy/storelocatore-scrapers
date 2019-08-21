const Apify = require('apify');

const {
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  countrySelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hoursSelector,
} = require('./selectors');

const {
  enqueueStatePages,
  enqueueCityPages,
  enqueueDetailPages,
} = require('./routes');

const {
  formatHours,
  clipStoreNumber,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'http://locations.goldenchick.com/',
    userData: {
      urlType: 'initial',
    },
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    handlePageFunction: async ({
      request, $,
    }) => {
      if (request.userData.urlType === 'initial') {
        await enqueueStatePages({ $ }, { requestQueue });
        await enqueueDetailPages({ $ }, { requestQueue });
      }
      if (request.userData.urlType === 'state') {
        await enqueueCityPages({ $ }, { requestQueue });
        await enqueueDetailPages({ $ }, { requestQueue });
      }
      if (request.userData.urlType === 'city') {
        await enqueueDetailPages({ $ }, { requestQueue });
      }
      if (request.userData.urlType === 'detail') {
        /* eslint-disable camelcase */
        const storeUrl = request.url;
        const store_number = clipStoreNumber(storeUrl);
        const location_name = $(locationNameSelector).attr('content');
        const street_address = $(streetAddressSelector).attr('content');
        const city = $(citySelector).attr('content');
        const state = $(stateSelector).attr('content');
        const zip = $(zipSelector).attr('content');
        const country_code = $(countrySelector).attr('content');
        const phone = $(phoneSelector).attr('content');
        const latitude = $(latitudeSelector).attr('content');
        const longitude = $(longitudeSelector).attr('content');
        const hours = $(hoursSelector).text();

        const poiData = {
          locator_domain: 'goldenchick_com',
          location_name,
          street_address,
          city,
          state,
          zip,
          country_code,
          store_number,
          phone,
          latitude,
          longitude,
          hours_of_operation: formatHours(hours),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();
});
