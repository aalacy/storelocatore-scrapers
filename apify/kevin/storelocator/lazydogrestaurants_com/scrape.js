const Apify = require('apify');
const {
  utils: { enqueueLinks },
} = Apify;

function countUnique(iterable) {
  return new Set(iterable).size;
}

function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}
const sleep = async () => {
  const ms = randomIntFromInterval(1000, 5000);
  console.log('sleeping ' + ms + 'ms');
  return Apify.utils.sleep(ms);
};

const parseCityStateZip = (str) => {
  const returnObj = {
    city: null, 
    state: null, 
    zip: null
  };
  const match = str.match(/^(.+),\s+?(\w{2})\s+?(\d{5}(-\d{4})?)/);
  if (match) {
    returnObj.city = match[1].trim();
    returnObj.state = match[2].trim();
    returnObj.zip = match[3].trim();
  }
  return returnObj;
}

const getAddress = ($locationDiv) => {
  const returnObj = {
    street_address: '<MISSING>',
    city: '<MISSING>', 
    state: '<MISSING>', 
    zip: '<MISSING>'
  };

  let $addressBlock = $locationDiv.children('p').eq(0);

  const $addressTextNodes = 
      $addressBlock
        .contents()
        .filter(function() {
          return this.type === 'text'; 
        });

  returnObj.street_address = $addressTextNodes.eq(1).text().trim();

  const cityStateZip = $addressTextNodes.eq(2).text().trim();
  Object.assign(returnObj, parseCityStateZip(cityStateZip));

  return returnObj;
}

const getHours = ($locationDiv, $) => {
  let hours = [];

  const $firstStrong = $locationDiv.children('strong').eq(0);

  const $nextNodes = $firstStrong.nextUntil('a');

  let str = '';
  $nextNodes.each((index, elem) => {
    if (elem.name === 'strong') {
      hours.push(str);
      str = $(elem).text().trim() + ' ';
    } else if (elem.next.data) {
      const trimmed =  elem.next.data.trim();
      if (trimmed.length) {
        str += trimmed + ', ';
      }
    }
  });
  hours.push(str);

  return hours.length ? hours.join(' ') : '<MISSING>';
}

const parseLocation = async $ => {
  const loc = {
    locator_domain: 'lazydogrestaurants.com',
    location_name: null,
    street_address: null,
    city: null,
    state: null,
    zip: null,
    country_code: '<MISSING>',
    store_number: '<MISSING>',
    phone: null,
    location_type: '<MISSING>',
    latitude: '<MISSING>',
    longitude: '<MISSING>',
    hours_of_operation: null,
  }; 

  const $locationDiv = $('div.location-item');

  loc.location_name = $locationDiv.find('h2').text().trim();

  Object.assign(loc, getAddress($locationDiv));

  loc.location_name = `${loc.city}, ${loc.state} - ${loc.location_name}`;

  loc.phone = $locationDiv.find('a.telephone').text().trim() || '<MISSING>';

  loc.hours_of_operation = getHours($locationDiv, $);

  return loc;
};


(async () => {
  const initialUrl = 'https://www.lazydogrestaurants.com/locations';

  const userAgent =
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' +
    ' Chrome/75.0.3770.100 Safari/537.36';

  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: initialUrl,
    headers: {
      'user-agent': userAgent,
    }
  });

  const isComingSoonLocation = $optionElem => 
    $optionElem.text().includes('coming soon');

  const handlePageFunction = async ({ request, response, html, $ }) => {

    console.log(`Got ${request.url}`);

    if (request.userData.isLocationDetailPage) {

      const location = await parseLocation($);
      console.log(location);
      await Apify.pushData(location);
      await sleep();

    } else {

      const $locationSelectOptions = $('#selectLocation option[value]');
      console.log(`>>> found ${$locationSelectOptions.length} total location options`);

      const $comingSoonLocationUrls = [];
      const $queuedLocationUrls = [];

      $locationSelectOptions.each((i, optionElem) => {

        const $optionElem = $(optionElem);
        const locationUrl = $optionElem.attr('value');
        
        // ignore coming-soon locations
        if (isComingSoonLocation($optionElem)) {

          console.log('skipping coming-soon location: ' + locationUrl);
          $comingSoonLocationUrls.push(locationUrl);

        } else {
          
          console.log('queuing up: ' + locationUrl);
          requestQueue.addRequest({
            url: locationUrl,
            headers: {
              'user-agent': userAgent
            },
            userData: {
              isLocationDetailPage: true
            }
          });

          $queuedLocationUrls.push(locationUrl);

        }
      });

      console.log(`Total coming-soon locations skipped: ${$comingSoonLocationUrls.length}`);
      console.log(`Total queued-up locations to scrape: ${$queuedLocationUrls.length}`);
      console.log(`Count of unique queued up URLs: ${countUnique($queuedLocationUrls)}`);

      await sleep();
    }
  };

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    handlePageFunction,
  });

  await crawler.run();
})();
