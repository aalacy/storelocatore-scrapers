const Apify = require('apify');
const {
  utils: { enqueueLinks },
} = Apify;

function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}
const sleep = async () => {
  const ms = randomIntFromInterval(1000, 5000);
  console.log('sleeping ' + ms + 'ms');
  return Apify.utils.sleep(ms);
};

function countUnique(iterable) {
  return new Set(iterable).size;
}

const parseCityState = (str) => {
  const returnObj = {
    city: '<MISSING>', 
    state: '<MISSING>'
  }
  const match = str.match(/^(.+), (\w{2})/);
  if (match) {
    returnObj.city = match[1].trim();
    returnObj.state = match[2].trim();
  }
  return returnObj;
};

const parseZip = (str) => {
  let zip = null;
  const match = str.match(/(\d{5}(-\d{4})?)/);
  if (match) {
    zip = match[1].trim();
  }
  return zip || '<MISSING>';
}

const getAddress = ($locationDiv) => {
  const returnObj = {
    street_address: '<MISSING>',
    city: '<MISSING>', 
    state: '<MISSING>', 
    zip: '<MISSING>'
  };

  let $addressBlock = $locationDiv.find('.map-info-address');

  // sometimes the address is wrapped in an anchor tag
  const $addressParentA = $addressBlock.find('a');
  if ($addressParentA.length > 0) {
    $addressBlock = $addressParentA;
  }

  // try to get the city and state from the span.map-info-city, 
  //  but not all location detail pages have this element. in that case
  //  we'll have to parse it from the following span.map-info-address
  const $cityState = $locationDiv.find('.map-info-city');
  if ($cityState.length){
    Object.assign(returnObj, parseCityState($cityState.text().trim()));
  } 

  const $addressTextNodes = 
      $addressBlock
        .contents()
        .filter(function() {
          return this.type === 'text'; 
        });

  returnObj.street_address = $addressTextNodes.eq(0).text().trim();

  // the next text node might be line 2 of the address, or it might be the city, state zip
  const cityStateZipOrAddressLine2 = $addressTextNodes.eq(1).text().trim();
  switch ($addressTextNodes.length) {
    case 2: 
      // should be the city, state, and zip.
      // we might already have the city and state, but if not ...
      if (returnObj.city === '<MISSING>' || returnObj.state === '<MISSING>') {
        Object.assign(returnObj, parseCityState(cityStateZipOrAddressLine2));
      }
      returnObj.zip = parseZip(cityStateZipOrAddressLine2);
      break;
    case 3: 
      // should be the address line 2
      returnObj.street_address += ', ' + cityStateZipOrAddressLine2;
      const cityStateZip = $addressTextNodes.eq(2).text().trim();
      // we might already have the city and state, but if not ...
      if (returnObj.city === '<MISSING>' || returnObj.state === '<MISSING>') {
        Object.assign(returnObj, parseCityState(cityStateZip));
      }
      returnObj.zip = parseZip(cityStateZip);
      break;
  }

  return returnObj;
}

const parseLocation = async $ => {
  const loc = {
    locator_domain: 'duckdonuts.com',
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

  const $locationDiv = $('#duckMapLocation');

  loc.location_name = $locationDiv.find('.map-info-title').text().trim();

  Object.assign(loc, getAddress($locationDiv));

  const data = $locationDiv.data();
  loc.latitude = data.lat;
  loc.longitude = data.lng;

  loc.phone = $locationDiv.find('.location-page-phone').text().trim() || '<MISSING>';

  let hours = [];
  $('.single-location__hours--row').each((i, elem) => {
    $elem = $(elem);
    const day = $elem.find('.single-location__hours--day').text().trim();
    const open = $elem.find('.single-location__hours--open').text().trim();
    const close = $elem.find('.single-location__hours--close').text().trim();
    hours.push(`${day}: ${open} - ${close}`);
  });

  loc.hours_of_operation = hours.length ? hours.join(', ') : '<MISSING>';

  return loc;
};

(async () => {
  const initialUrl = 'https://www.duckdonuts.com/locations/';

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

  const isComingSoonLocation = $mapPinImgElem => 
    $mapPinImgElem.attr('src').includes('map-pin-soon');

  const handlePageFunction = async ({ request, response, html, $ }) => {

    console.log(`Got ${request.url}`);

    if (request.userData.isLocationDetailPage) {

      const location = await parseLocation($);
      console.log(location);
      await Apify.pushData(location);
      await sleep();

    } else {

      //console.log('>>> looking at map pins on initial page ...');

      const $mapPins = $('#synMap img.syn-marker-icon');
      //console.log(`>>> found ${$mapPins.length} total pins`);

      const $comingSoonLocationUrls = [];
      const $queuedLocationUrls = [];

      $mapPins.each((i, mapPinImgElem) => {

        const $mapPinImgElem = $(mapPinImgElem);
        const locationUrl = $mapPinImgElem.parent('div').data().locationUrl;
        
        // ignore coming-soon locations
        if (isComingSoonLocation($mapPinImgElem)) {

          //console.log('skipping coming-soon location: ' + locationUrl);
          $comingSoonLocationUrls.push(locationUrl);

        } else {
          
          //console.log('queuing up: ' + locationUrl);
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
