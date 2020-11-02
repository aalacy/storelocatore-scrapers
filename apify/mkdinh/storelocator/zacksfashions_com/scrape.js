const Apify = require('apify');
const axios = require('axios');
const { decode } = require('js-base64');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

async function fetchLocationLinks({ $, requestQueue }) {
  const scriptLink = $('script[src*="storelocator"]').attr('src');
  const { data } = await axios.get(`https:${scriptLink}`);
  const [_, encodedData] = data.match(/store_render\s*=\s*["|'](.*?)["|']/i);
  const locations = JSON.parse(decode(encodedData));

  const promises = locations.map(async (location) => {
    const url = ['https://cazzapetitezacks.com/', location.url.replace(/^\/*/, '')].join('');
    const [street_address, city, state, zip, country_code] = location.address.split(', ');

    const userData = {
      locator_domain: 'cazzapetitezacks.com',
      page_url: url,
      location_name: getOrDefault(location.name.replace(/(Cazza Petite|Zacks)\s*-\s*/i, '')),
      location_type: MISSING,
      store_number: getOrDefault(location.id),
      street_address: getOrDefault(street_address),
      city: getOrDefault(city),
      state: getOrDefault(state),
      zip: getOrDefault(zip),
      country_code: getOrDefault(country_code.toUpperCase()),
      latitude: getOrDefault(location.lat),
      longitude: getOrDefault(location.lng),
      hours_of_operation: '',
      phone: getOrDefault(location.phone.replace(/\D/g, '')),
    };

    return requestQueue.addRequest({
      url,
      userData,
    });
  });

  await Promise.all(promises);
}

function parse({ $, request }) {
  const poi = request.userData;
  const hours = $('.table tr')
    .map(function () {
      const day = $(this);
      const dayName = day.find('th').text();
      const hours = day.find('td').text();
      return {
        day: dayName.trim(),
        hours: hours.trim(),
      };
    })
    .toArray();

  poi.hours_of_operation = JSON.stringify(hours);

  return poi;
}

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://cazzapetitezacks.com/apps/store-locator/all',
    userData: {
      pageType: 'locations',
    },
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    async handlePageFunction({ $, request }) {
      switch (request.userData.pageType) {
        case 'locations':
          await fetchLocationLinks({ $, requestQueue });
          break;
        default:
          const poi = parse({ $, request });
          await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();
});
