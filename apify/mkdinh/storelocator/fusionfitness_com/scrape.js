const Apify = require('apify');

const MISSING = '<MISSING>';

function parseLocation(location) {
  const { addressLine1, addressLine2, addressCountry, mapLat, mapLng } = location;
  const [city, state, zip] = addressLine2.split(', ');

  return {
    street_address: addressLine1,
    city,
    state,
    zip,
    country_code: addressCountry === 'United States' ? 'US' : addressCountry,
    latitude: mapLat,
    longitude: mapLng,
  };
}

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  requestQueue.addRequest({
    url: 'https://www.fusionfitness.com/locations',
    headers: {
      'User-Agent': 'request',
    },
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    async handlePageFunction({ $, request }) {
      const locations = $('.map-block');

      const pois = locations
        .map(function () {
          const location_name = $(this).prev().find('strong').text();

          const serializedData = $(this).attr('data-block-json');
          const { location } = JSON.parse(serializedData);
          const {
            street_address,
            city,
            state,
            zip,
            country_code,
            latitude,
            longitude,
          } = parseLocation(location);

          return {
            locator_domain: 'fusionfitness.com',
            page_url: request.url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            latitude,
            longitude,
            phone: MISSING,
            store_number: MISSING,
            location_type: MISSING,
            hours_of_operation: MISSING,
          };
        })
        .toArray();

      await Apify.pushData(pois);
    },
  });

  await crawler.run();
});
