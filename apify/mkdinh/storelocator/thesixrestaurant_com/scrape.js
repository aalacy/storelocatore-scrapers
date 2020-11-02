const Apify = require('apify');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  const data = typeof value === 'string' ? value.trim() : value;
  return data || MISSING;
}

async function enqueueLocationLinks({ $, requestQueue }) {
  return Apify.utils.enqueueLinks({
    $,
    requestQueue,
    selector: '.location-link',
    baseUrl: 'https://www.thesixrestaurant.com',
  });
}

async function scrape({ $, request }) {
  const locationName = $('#intro h1').text();
  const { street_address, city, state, zip, phone } = extractLocation($);
  const hoursOfOperation = extractHoursOfOperation($);
  return {
    locator_domain: 'thesixrestaurant.com',
    page_url: request.url,
    location_name: getOrDefault(locationName),
    location_type: MISSING,
    store_number: MISSING,
    street_address: getOrDefault(street_address),
    city: getOrDefault(city),
    state: getOrDefault(state),
    zip: getOrDefault(zip),
    country_code: 'US',
    latitude: MISSING,
    longitude: MISSING,
    phone: getOrDefault(phone),
    hours_of_operation: getOrDefault(hoursOfOperation),
  };
}

function extractLocation($) {
  const info = $('h1:contains(Hours)').siblings('p').last();
  const address = info.find('a:nth-of-type(1)').text().trim();
  const phoneNumber = info.find('a:nth-of-type(2)').text().trim();
  return {
    ...parseAddress(address),
    phone: formatPhoneNumber(phoneNumber),
  };
}

function parseAddress(address) {
  const [street_address, city, stateZip] = address.split(', ');
  const [state, zip] = stateZip.split(' ');
  return { street_address, city, state, zip };
}

function formatPhoneNumber(phoneNumber) {
  return phoneNumber.replace(/-/g, '');
}

function extractHoursOfOperation($) {
  // extracting starting and ending hours from text
  const HOURS_REGEX = /(\d\S*\s*(?:pm|am){1}).*?((?:\?$|\d\S*\s*(?:pm|am)(?!.*\?))(?!.*\1))/;
  const hoursOfOperation = [];
  const heading = $('h1:contains(Hours)');
  const dayHours = heading.siblings('p:nth-of-type(2)');
  const day = dayHours.find('strong').text().trim();
  const possibleHours = dayHours.clone().children().remove().end().text().trim();
  const hourText = possibleHours ? possibleHours : dayHours.next().text().trim();
  const matched = hourText.match(HOURS_REGEX);
  if (matched) {
    const [_, start, end] = matched;
    const hours = `${start.replace(/ /g, '')}-${end.replace(/ /g, '')}`;
    hoursOfOperation.push({ day, hours });
  } else {
    throw new Error('cannot parse hours');
  }

  // some locations has separate weekend hours
  const weekend = dayHours.siblings('p:nth-of-type(6)');
  if (weekend.length) {
    const weekendDay = weekend.find('strong').text().trim();
    let weekendHourText = weekend.clone().children().remove().end().text().trim();
    // some times there are features information attached to hours
    const matched = weekendHourText.match(HOURS_REGEX);
    if (matched) {
      const [_, weekendStart, weekendEnd] = matched;
      const weekendHours = `${weekendStart.replace(/ /g, '')}-${weekendEnd.replace(/ /g, '')}`;
      hoursOfOperation.push({ day: weekendDay, hours: weekendHours });
    } else {
      throw new Error('cannot parse hours');
    }
  }
  return JSON.stringify(hoursOfOperation);
}

Apify.main(async function () {
  const url = 'http://www.thesixrestaurant.com/locations/';
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url,
    userData: {
      pageType: 'locations',
    },
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    async handlePageFunction({ $, request }) {
      switch (request.userData.pageType) {
        case 'locations':
          await enqueueLocationLinks({ $, requestQueue });
          break;
        default:
          const poi = await scrape({ $, request });
          await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();
});
