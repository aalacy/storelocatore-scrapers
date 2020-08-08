const Apify = require('apify');
const axios = require('axios');

const MISSING = '<MISSING>';

function getOrDefault(value) {
  return value || MISSING;
}

function extractHoursOfOperationForLocation(storeName, $) {
  const days = $(`.mp-detail-info:contains(${storeName}) .mp-openday-list tr`);
  console.log;
  const hoursOfOperations = days
    .map(function () {
      const row = $(this);
      const day = row.find('.mp-openday-list-title').text().trim();
      const hours = row.find('.mp-openday-list-value').text().trim();
      return `${day} ${hours}`;
    })
    .toArray();

  return hoursOfOperations.join(',');
}

Apify.main(async () => {
  const baseUrl = 'https://lacrosseunlimited.com';
  const locationDataUrl = `${baseUrl}/mpstorelocator/storelocator/locationsdata`;
  const locationUrl = `${baseUrl}/store-locator`;

  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: locationUrl,
  });
  const { data } = await axios.get(locationDataUrl);

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    async handlePageFunction({ $ }) {
      const pois = data.map((location) => {
        return {
          locator_domain: 'lacrosseunlimited.com',
          page_url: locationUrl,
          store_number: getOrDefault(location.id),
          location_name: getOrDefault(location.name),
          street_address: getOrDefault(location.street),
          state: getOrDefault(location.state),
          city: getOrDefault(location.city),
          zip: getOrDefault(location.postal),
          country_code: getOrDefault(location.country),
          latitude: getOrDefault(location.lat),
          longitude: getOrDefault(location.lng),
          phone: getOrDefault(location.phone1),
          hours_of_operation: getOrDefault(extractHoursOfOperationForLocation(location.name, $)),
          location_type: MISSING,
        };
      });

      await Apify.pushData(pois);
    },
  });

  await crawler.run();
});
