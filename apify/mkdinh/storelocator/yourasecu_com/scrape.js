const Apify = require('apify');
const request = require('request');
const cheerio = require('cheerio');

var url = 'https://yourasecu.com/locations';
async function scrape() {
  return new Promise(async (resolve, reject) => {
    request(url, (err, res, html) => {
      if (!err && res.statusCode == 200) {
        const $ = cheerio.load(html);
        var items = [];

        function mainhead(i) {
          if (9 > i) {
            var location_name = $('.container').find('.branchTitle').find('h1').eq(i).text();
            var address_tmp = $('.container')
              .find('.row ')
              .find('.six:first-child')
              .eq(i)
              .html()
              .trim();
            var address_tmp1 = address_tmp.split('<br>');
            var address = address_tmp1[1].replace(/\r?\n/g, '');

            var state_tmp = address_tmp1[2];
            var state_tmp1 = state_tmp.split(' ');
            var city = state_tmp1[0].replace(',', '').replace(/\r?\n/g, '');
            var state = state_tmp1[1];
            var zip = state_tmp1[2];
            var phone = address_tmp1[3]
              .replace(/<[^>]*>?/gm, '')
              .replace('Phone:', '')
              .replace(/\r?\n/g, '')
              .trim();
            var latitude_tmp = $('.container')
              .find('.row ')
              .find('.six:first-child')
              .eq(i)
              .find('a:nth-child(2)')
              .attr('href');
            var latitude_tmp1 = latitude_tmp.split(',');
            var latitude_tmp2 = latitude_tmp1[2].split('/@');
            var latitude = latitude_tmp2[1];
            var longitude = latitude_tmp1[3];

            var hour_tmp = $('.container')
              .find('.row ')
              .find('.six:nth-child(2)')
              .eq(i)
              .html()
              .trim();
            var hour_tmp1 = hour_tmp.split('</p>');
            var hour1 = hour_tmp1[0]
              .replace(/<[^>]*>?/gm, '')
              .replace('Lobby Hours', '')
              .replace('Hours', '')
              .replace(/\r?\n/g, '');

            items.push({
              locator_domain: 'https://yourasecu.com/',

              location_name: location_name,

              street_address: address,

              city: city,

              state: state,

              zip: zip,

              country_code: 'US',

              store_number: '<MISSING>',

              phone: phone,

              location_type: 'yourasecu',

              latitude: latitude,

              longitude: longitude,

              hours_of_operation: hour1,
            });

            mainhead(i + 1);
          } else {
            resolve(items);
          }
        }

        mainhead(0);
      }
    });
  });
}

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

function parseAddress(address) {
  const cleaned = address.replace(/\+/g, ' ');
  const components = cleaned.split(', ');
  components.shift(); // remove location name
  const country_code = components.pop();
  const [state, zip] = components.pop().split(' ');
  const city = components.pop();
  const street_address = components.join(', ');

  return {
    street_address,
    city,
    state,
    zip,
    country_code: country_code.match(/usa/i) ? 'US' : country_code,
  };
}

function formatPhone(phone) {
  const REMOVAL_REGEX = /(Phone\:\s*)|\-/g;
  return phone.replace(REMOVAL_REGEX, '');
}

function extractAddressFromGoogleLink(googleLink) {
  const [_, addressLine, latitude, longitude] = googleLink.match(/dir\/\/(.*?)\/@(.*?),(.*?),/);
  const address = parseAddress(addressLine);
  return { ...address, latitude, longitude };
}

function extractHoursOfOperation(content) {
  const HOURS_REGEX = /.*?Lobby Hours\s+(.*?)(?:Drive-thru Hours\s+(.*?))?$/;
  const cleaned = content.trim().replace(/\n|\s\s+/g, ' ');
  const [_, lobby, driveThru] = cleaned.match(HOURS_REGEX);

  return JSON.stringify({ lobby, driveThru });
}

Apify.main(async () => {
  const locationUrl = 'https://yourasecu.com/locations';
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: locationUrl,
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    async handlePageFunction({ $, request }) {
      const locations = $('.location-block');

      const pois = locations
        .map(function () {
          const loc = $(this);
          const details = loc.find('.liquid-lp-excerpt p');

          const phone = formatPhone(details.eq(1).text());
          const location_name = loc.find('.liquid-lp-title').text();
          const hours_of_operation = extractHoursOfOperation(loc.find('.lqd-modal-content').text());

          const {
            street_address,
            city,
            state,
            zip,
            country_code,
            latitude,
            longitude,
          } = extractAddressFromGoogleLink(loc.find('.btn-location').attr('href'));

          return {
            locator_domain: 'yourasecu.com',
            page_url: request.url,
            location_name: getOrDefault(location_name),
            street_address: getOrDefault(street_address),
            city: getOrDefault(city),
            state: getOrDefault(state),
            zip: getOrDefault(zip),
            country_code: getOrDefault(country_code),
            phone: getOrDefault(phone),
            latitude: getOrDefault(latitude),
            longitude: getOrDefault(longitude),
            hours_of_operation: getOrDefault(hours_of_operation),
            location_type: MISSING,
            store_number: MISSING,
          };
        })
        .toArray();

      await Apify.pushData(pois);
    },
  });

  await crawler.run();
});
