const Apify = require('apify');
const { Poi } = require('./Poi');

function parseAddress(address) {
  const cleanedAddress= address.replace(/\s\s+/g, '\n').replace(/\,/g, '').trim();
  return cleanedAddress.split('\n');
}

function extractHoursOfOperation(hours, $) {
  const items = hours.children();
  const hoursOfOperation = items.map(function() {
    const item = $(this);
    const day = item.find('span:nth-child(1)').text().trim().replace(/–|&/g, '-');
    const hours = item.find('span:nth-child(2)').text().trim().replace(/ to /g, ' - ');
    return `${day} ${hours}`;
  }).toArray();
  return hoursOfOperation.join(',')
}

function formatPhoneNubmer(phoneNumber) {
  const REMOVE_CHAR_REGEX = /\(|\)|\-/g;
  return phoneNumber.replace(REMOVE_CHAR_REGEX, '');
}

Apify.main(async () => {
  const locator_domain = 'ezellschicken.com';
  const page_url = 'https://ezellschicken.com/locations';

  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: page_url,
    headers: {
      'User-Agent': 'request',
    },
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    async handlePageFunction({ $ }) {
      const locations  = $('.location');
      const pois = locations.map(function() {
        const loc = $(this);
        const location_name = loc.attr('data-name');
        const store_number = loc.attr('data-target').split('-')[1];
        const latitude = loc.attr('data-location-lat');
        const longitude = loc.attr('data-location-lng');

        const address = loc.find('.location-address').text();
        const [ street_address, city, state, zip ] = parseAddress(address);
        const country_code = 'US'

        const hours = loc.find('.hours-inner');
        const hours_of_operation = extractHoursOfOperation(hours, $);

        const phoneNumber = loc.find('a').first().text();
        const phone = formatPhoneNubmer(phoneNumber);
        
        return new Poi({
          locator_domain,
          page_url,
          location_name,
          store_number,
          street_address,
          city,
          state,
          zip,
          country_code,
          latitude,
          longitude,
          hours_of_operation,
          phone
        })
      }).toArray();

      await Apify.pushData(pois);
    }
  });

  await crawler.run();
});
