const Apify = require('apify');
const fs = require('fs');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

Apify.main(async function () {
  const requestList = await Apify.openRequestList('locations', [
    {
      url: 'https://stores.cabelas.com/',
    },
  ]);

  const crawler = new Apify.CheerioCrawler({
    requestList,
    async handlePageFunction({ $, request }) {
      const geoData = JSON.parse($('#js-map-config-dir-map').html());
      const storeMap = geoData.locs.reduce((map, store) => {
        map[store.id] = store;
        return map;
      }, {});

      const locations = $('.CountryLocations-item');
      const pois = locations
        .map(function () {
          const card = $(this);
          const storeNumber = card.attr('id').replace(/[^0-9]/g, '');
          const geolocation = storeMap[parseInt(storeNumber)];
          const locationName = card.find('.location-name-geo-inline').text().trim();
          const locationHours = card.find('[data-days]').attr('data-days');
          const hoursOfOperation = JSON.parse(locationHours).map((dayHours) => ({
            day: dayHours.day,
            start: dayHours.intervals[0].start,
            end: dayHours.intervals[0].end,
          }));

          const streetAddress = card.find('.c-address-street-1').text().trim();
          const city = card.find('.c-address-city').text().trim().replace(/,$/, '');
          const state = card.find('.c-address-state').text().trim();
          const zip = card.find('.c-address-postal-code').text().trim();
          const countryCode = card.find('.c-address-country-name').text().trim();
          const latitude = geolocation.latitude;
          const longitude = geolocation.longitude;

          const phone = card
            .find('span[itemprop=telephone]')
            .first()
            .text()
            .trim()
            .replace(/[^0-9]/g, '');

          return {
            locator_domain: 'cabelas.com',
            page_url: request.url,
            location_name: getOrDefault(locationName),
            location_type: MISSING,
            store_number: getOrDefault(storeNumber),
            street_address: getOrDefault(streetAddress),
            city: getOrDefault(city),
            state: getOrDefault(state),
            zip: getOrDefault(zip),
            country_code: getOrDefault(countryCode),
            latitude: getOrDefault(latitude),
            longitude: getOrDefault(longitude),
            hours_of_operation: getOrDefault(JSON.stringify(hoursOfOperation)),
            phone: getOrDefault(phone),
          };
        })
        .toArray();

      const csv = pois.map((poi) => Object.values(poi).join(',')).join('\n');

      fs.writeFile(__dirname + '/data.csv', csv, () => {
        console.log('done');
      });

      await Apify.pushData(pois);
    },
  });

  await crawler.run();
});
