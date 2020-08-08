const Apify = require('apify');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

function parseAddress(address) {
  const components = address.split(', ');
  const stateAndZip = components.pop();
  const [state, zip] = stateAndZip.split([' ']);
  const city = components.pop();
  const street_address = components.join(', ');
  const country_code = 'US';

  return { street_address, city, state, zip, country_code };
}

function formatPhone(phone) {
  const REMOVAL_REGEX = /\(|\)|-|\./g;
  return phone.replace(REMOVAL_REGEX, '');
}

Apify.main(async () => {
  const locationUrl = 'https://www.cafegratitude.com/locations';

  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: locationUrl,
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    async handlePageFunction({ $, request }) {
      const locations = $('.sqs-col-5');
      const pois = locations
        .map(function () {
          const loc = $(this);
          const location_name = loc.find('h3').text();

          const content = loc.find('.sqs-block-content').last().find('p');
          const { street_address, city, state, zip, country_code } = parseAddress(
            content.eq(0).text()
          );

          const phone = formatPhone(content.eq(1).text());
          const hours_of_operation = content.eq(2).text();

          return {
            locator_domain: 'cafegratitude.com',
            page_url: request.url,
            location_name: getOrDefault(location_name),
            street_address: getOrDefault(street_address),
            city: getOrDefault(city),
            state: getOrDefault(state),
            zip: getOrDefault(zip),
            country_code: getOrDefault(country_code),
            phone: getOrDefault(phone),
            hours_of_operation: getOrDefault(hours_of_operation),
            store_number: MISSING,
            location_type: MISSING,
            latitude: MISSING,
            longitude: MISSING,
          };
        })
        .toArray();

      await Apify.pushData(pois);
    },
  });

  await crawler.run();
});
