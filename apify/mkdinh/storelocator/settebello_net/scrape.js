const Apify = require('apify');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  if (typeof value === 'string') {
    value = value.trim();
  }
  return value || MISSING;
}

function extractCityStateZip(text) {
  const cleaned = text.replace(/\|/g, '').trim();
  const [city, stateZip] = cleaned.split(', ');
  const [state, zip] = stateZip.split(' ');
  const country_code = city && state && zip ? 'US' : null;
  return { city, state, zip, country_code };
}

function extractLatLng(googleLink) {
  const matched = googleLink.match(/\/@(.*?),(.*?),/);
  return {
    latitude: matched ? matched[1].trim() : null,
    longitude: matched ? matched[2].trim() : null,
  };
}

function extractHoursOfOperation(jObjects, $) {
  const hours = jObjects
    .map(function () {
      return $(this).text().trim().replace(/\s\s+/g, ' ');
    })
    .toArray()
    .filter((hours) => hours);

  return hours.length > 1 ? hours.join(',') : hours[0];
}

function formatPhone(phoneNumber) {
  return phoneNumber.replace(/\./g, '').trim();
}

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.settebello.net/locations',
    headers: {
      'user-agent': 'request',
    },
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    async handlePageFunction({ $, request }) {
      const infos = $('.sqs-block-content').has('h3');

      const pois = infos
        .map(function () {
          const info = $(this);
          const location_name = info.find('h3').text();
          const street_address = info.find('p:nth-of-type(1)').text();

          const cityStateZip = info
            .find('p:nth-of-type(2)')
            .clone()
            .children()
            .remove()
            .end()
            .text();
          const { city, state, zip, country_code } = extractCityStateZip(cityStateZip);

          const googleLink = info.find('p:nth-of-type(2) a').attr('href');
          const { latitude, longitude } = extractLatLng(googleLink);

          const phoneNumber = info.find('p:nth-of-type(3)').text();
          const phone = formatPhone(phoneNumber);

          const hours = info.find('p').slice(3);
          const hours_of_operation = extractHoursOfOperation(hours, $);

          return {
            locator_domain: 'settebello.net',
            page_url: request.url,
            location_name: getOrDefault(location_name),
            street_address: getOrDefault(street_address),
            city: getOrDefault(city),
            state: getOrDefault(state),
            zip: getOrDefault(zip),
            country_code: getOrDefault(country_code),
            latitude: getOrDefault(latitude),
            longitude: getOrDefault(longitude),
            phone: getOrDefault(phone),
            store_number: MISSING,
            location_type: MISSING,
            hours_of_operation: getOrDefault(hours_of_operation),
          };
        })
        .toArray();

      await Apify.pushData(pois);
    },
  });

  await crawler.run();
});
