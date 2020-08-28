const Apify = require('apify');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

Apify.main(async () => {
  const requestList = await Apify.openRequestList('locations', [
    {
      url: 'http://www.charochicken.com/locations/',
    },
  ]);

  const crawler = new Apify.CheerioCrawler({
    requestList,
    async handlePageFunction({ $, request }) {
      const locations = $('iframe')
        .map(function () {
          const iframe = $(this);
          return iframe.attr('aria-label');
        })
        .toArray();

      const pois = locations.map((location) => {
        const [address, phone] = location.split(' (');
        const phoneNumber = phone ? phone.replace(/\D/g, '') : null;
        const [streetAddressAndCity, stateAndZip] = address.split(', ');

        const splitted = streetAddressAndCity.split(/\s\s+/);
        if (splitted.length === 3) {
          splitted.shift(); // some address has the city name prefixed
        }

        const [streetAddress, city] = splitted;
        const [state, zip] = stateAndZip.split(' ');

        const CITY_REGEX = new RegExp(`\s*${city}\s*`);
        const cleaned_address = streetAddress.replace(CITY_REGEX, '').trim();

        return {
          locator_domain: 'charochicken.com',
          page_url: request.url,
          location_name: getOrDefault(city),
          location_type: MISSING,
          store_number: MISSING,
          street_address: getOrDefault(cleaned_address),
          city: getOrDefault(city),
          state: getOrDefault(state),
          zip: getOrDefault(zip),
          country_code: 'US',
          latitude: MISSING,
          longitude: MISSING,
          phone: getOrDefault(phoneNumber),
          hours_of_operation: MISSING,
        };
      });

      await Apify.pushData(pois);
    },
  });

  await crawler.run();
});
