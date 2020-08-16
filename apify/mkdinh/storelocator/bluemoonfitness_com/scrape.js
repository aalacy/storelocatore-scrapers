const Apify = require('apify');
const axios = require('axios');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

function parseAddress(text) {
  const address = text.replace(/^,|,$|,,/g, '');
  const components = address.split(',');
  const zipState = components.pop().trim();
  const [zip, state] = zipState.split(' ');
  const city = components.pop();
  const street_address = components.join(',');
  const country_code = 'US';

  return {
    street_address: street_address.trim(),
    city: city.trim(),
    state: state.trim(),
    zip: zip.trim(),
    country_code,
  };
}

function formatPhoneNumber(phoneNumber) {
  return phoneNumber.replace(/\.|\s|\(|\)|\-/g, '');
}

function extractDetails(pin) {
  const latitude = pin.attr('data-lat');
  const longitude = pin.attr('data-lng');

  const addressAndPhone = pin.find('.infowindow p:nth-of-type(1)');
  addressAndPhone.find('br').replaceWith(',');

  const addressSpan = addressAndPhone.find('.section-info-text');
  const address = addressSpan.length
    ? addressSpan.text()
    : addressAndPhone.clone().children().remove().end().text();

  const phoneNumber = addressAndPhone.find('a').last().text();
  const phone = formatPhoneNumber(phoneNumber);

  const { street_address, city, state, zip, country_code } = parseAddress(address);
  return { street_address, city, state, zip, country_code, latitude, longitude, phone };
}

async function fetchHoursOfOperation(link, $) {
  const { data } = await axios.get(link);

  const details = $(data);
  const hoursDetails = details.find('h3:contains("Hours of Operation")').nextAll('p');
  const hours_of_operations = hoursDetails
    .map(function () {
      const day = $(this).find('strong').text().trim();
      const hours = $(this).clone().children().remove().end().text().trim();
      return day && hours ? { day, hours } : null;
    })
    .toArray()
    .filter((hour) => hour);

  return JSON.stringify(hours_of_operations);
}

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://bluemoonfitness.com/locations',
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    async handlePageFunction({ $, request }) {
      const promises = $('.et_pb_map_pin')
        .map(async function () {
          const pin = $(this);
          const link = pin.find('a').last().attr('href');
          const location_name = pin
            .attr('data-title')
            .replace(/location/i, '')
            .trim();

          const {
            street_address,
            city,
            state,
            zip,
            country_code,
            latitude,
            longitude,
            phone,
          } = extractDetails(pin);

          const storeLink = 'https://bluemoonfitness.com' + link;
          const hours_of_operations = await fetchHoursOfOperation(storeLink, $);

          return {
            locator_domain: 'bluemoonfitness.com',
            page_url: storeLink,
            location_name: getOrDefault(location_name),
            location_type: MISSING,
            store_number: MISSING,
            street_address: getOrDefault(street_address),
            city: getOrDefault(city),
            state: getOrDefault(state),
            zip: getOrDefault(zip),
            country_code: getOrDefault(country_code),
            latitude: getOrDefault(latitude),
            longitude: getOrDefault(longitude),
            phone: getOrDefault(phone),
            hours_of_operations: getOrDefault(hours_of_operations),
          };
        })
        .toArray();

      const pois = await Promise.all(promises);
      await Apify.pushData(pois);
    },
  });

  await crawler.run();
});
