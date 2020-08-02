const Apify = require('apify');
const MISSING = '<MISSING>';

function getName(section) {
  const name = section.find('.et_pb_text_inner h2').text();
  return name;
}

function getDetails(section) {
  const returnRegex = /\r\n?|\n/g;
  const locationInfo = section.find('.locationCols li').text().replace(returnRegex, ' ').trim();
  const [_, address, phone] = locationInfo.trim().match(/\s*(.*?)Phone:\s*(.*$)/);

  const googleLink = section.find('a:contains("Directions")').attr('href');

  return {
    ...parseAddress(address),
    ...parseLatLongFromGoogleLink(googleLink),
    phone: formatPhone(phone),
  };
}

function formatPhone(phoneNumber) {
  return phoneNumber.replace(/\s|\(|\)|\-/g, '');
}

function parseLatLongFromGoogleLink(link) {
  const matched = link.match(/@(.*?),(.*?),/);
  if (matched) {
    const [_, lat, long] = matched;
    return { lat, long };
  }

  return { lat: null, long: null };
}

function parseAddress(address) {
  const [addressLine, stateAndZip] = address.split(',');
  let parts = addressLine.trim().split(' ');
  let city = parts.pop();
  let street_address = parts.join(' ');

  // in some cases the rd. are joined together with the city name when scraping
  if (city.match(/(.*?\.)(.*)/)) {
    const [_, address_type, cityName] = city.match(/(.*?\.)(.*)/);
    street_address = `${street_address} ${address_type}`;
    city = cityName;
  }

  const stateAndZipParts = stateAndZip.trim().split(' ');
  const zip = stateAndZipParts.pop();
  const state = stateAndZipParts.join(' ');

  return { street_address, city, state, zip };
}

Apify.main(async () => {
  // Begin scraper
  const requestList = await Apify.openRequestList('black-stone-steak-house', [
    'https://blackstonesteakhouse.com/locations/',
  ]);

  const crawler = new Apify.CheerioCrawler({
    requestList,
    async handlePageFunction({ $ }) {
      const locations = $('.et_pb_row');

      const data = locations
        .map(function () {
          const section = $(this);

          const name = getName(section);
          if (!name) return; // should always have name with location

          const { street_address, city, state, zip, phone, lat, long } = getDetails(section);
          return {
            locator_domain: 'blackstonesteakhouse.com',
            location_name: name || MISSING,
            street_address: street_address || MISSING,
            city: city || MISSING,
            state: state || MISSING,
            zip: zip || MISSING,
            country_code: 'US',
            store_number: MISSING,
            phone: phone || MISSING,
            location_type: MISSING,
            latitude: lat || MISSING,
            longitude: long || MISSING,
            hours_of_operation: MISSING,
          };
        })
        .toArray();

      await Apify.pushData(data);
    },
  });

  await crawler.run();
  // End scraper
});
