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

function parseAddress(address) {
  const components = address.split(/,/g);
  const isCitySplitted = components.length > 2;
  const cityStateZip = components.pop().split(' ');
  const zip = cityStateZip.pop();
  const state = cityStateZip.pop();
  const city = isCitySplitted ? components.pop() : cityStateZip.join(' ').replace(/,$/, '');

  const street_address = components.join(' ');
  return { street_address, city, state, zip };
}

function extractLocationInfo(locInfo) {
  const REMOVE_BREAK_TAG_REGEX = /<br>/g;
  const TRIM_COMMA_REGEX = /^,|,$/g;
  const location_name = locInfo.find('strong').text();
  const address = locInfo.find('p').clone().find('strong').remove().end().html();
  const cleaned = address.trim().replace(REMOVE_BREAK_TAG_REGEX, ',').replace(TRIM_COMMA_REGEX, '');
  const { street_address, city, state, zip } = parseAddress(cleaned);
  return { location_name, street_address, city, state, zip };
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
          const locInfo = $(this).prev();

          const serializedData = $(this).attr('data-block-json');
          const { location } = JSON.parse(serializedData);
          const { country_code, latitude, longitude } = parseLocation(location);

          const { location_name, street_address, city, state, zip } = extractLocationInfo(locInfo);

          return {
            locator_domain: 'fusionfitness.com',
            page_url: request.url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            latitude: latitude,
            longitude: longitude,
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
