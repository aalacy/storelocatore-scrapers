const Apify = require('apify');
const {
  utils: { enqueueLinks },
} = Apify;

const log = async (currentUrl, locationsArray) => {
  console.log('\n-----\n');
  console.log(`Got ${currentUrl}`);
  if (locationsArray) {
    console.log(`Found ${locationsArray.length} locations`);
  }
  console.log('\n-----\n');
};

function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}

const sleep = async () => {
  const ms = randomIntFromInterval(1000, 5000);
  console.log('sleeping ' + ms + 'ms');
  return Apify.utils.sleep(ms);
};

const parseAddress = (address) => {
  const addy = { 
    street: null, 
    city: null, 
    state: null, 
    zip: null
  };
  const match = address.match(/^(.+?),(.+?),(.+?) (\d{5})/);
  if (match) {
    addy.street= match[1].trim();
    addy.city = match[2].trim();
    addy.state = match[3].trim();
    addy.zip = match[4].trim();
  }
  return addy;
}

const validLatitude = lat => {
  lat = parseFloat(lat);
  return -90.0 <= lat && lat <= 90.0;
};

const validLongitude = lon => {
  lon = parseFloat(lon);
  return -180.0 <= lon && lon <= 180.0;
};

const parseCorporateOffice = async ($, locationTemplate) => {
  const loc = Object.assign({}, locationTemplate);
  loc.location_name = 'Corporate Offices';

  const $parentDiv = $('.locationaddress-mob ');

  const address = $parentDiv.find('strong').text();
  const addressParsed = parseAddress(address);
  loc.street_address = addressParsed.street || '<MISSING>';
  loc.city = addressParsed.city || '<MISSING>';
  loc.state = addressParsed.state || '<MISSING>';
  loc.zip = addressParsed.zip || '<MISSING>';
  
  loc.phone = $parentDiv.find('a').eq(0).text();

  loc.fax = '<MISSING>';
  loc.latitude = '<MISSING>';
  loc.longitude = '<MISSING>';
  loc.hours_of_operation = '<MISSING>';
  loc.receiving_hours = '<MISSING>';
  
  return loc;
}

const parseLocations = async ($, locationTemplate) => {

  const locations = [];

  $('.BranchBizCard')
    .each((index, branchDiv) => {

      const $branchDiv = $(branchDiv);

      const loc = Object.assign({}, locationTemplate);

      loc.location_name = $branchDiv.find('a[itemprop="name"]').text();
      loc.street_address = $branchDiv.find('span[itemprop="streetAddress"]').text();
      loc.city = $branchDiv.find('span[itemprop="addressLocality"]').text();
      loc.state = $branchDiv.find('span[itemprop="addressRegion"]').text();
      loc.zip = $branchDiv.find('span[itemprop="postalCode"]').text();
      loc.phone = $branchDiv.find('span[itemprop="telephone"]').text();
      loc.fax = $branchDiv.find('span[itemprop="faxNumber"]').text();
      loc.latitude = $branchDiv.find('meta[itemprop="latitude"]').attr('content') || '<MISSING>';
      loc.longitude = $branchDiv.find('meta[itemprop="longitude"]').attr('content') || '<MISSING>';
      loc.hours_of_operation = $branchDiv.find('meta[itemprop="openingHours"]').attr('content') || '<MISSING>';
      loc.receiving_hours = $branchDiv.find('meta[itemprop="receivingHours"]').attr('content') || '<MISSING>'; 

      // validate range of latitude and longitude based on validate.py
      if ((typeof loc.latitude === 'number' && !validLatitude(loc.latitude)) 
        ||(typeof loc.longitude === 'number' && !validLongitude(loc.longitude))) {
        loc.latitude = '<INACCESSIBLE>';
        loc.longitude = '<INACCESSIBLE>';
      }

      locations.push(loc);

    });

  return locations;
};

const populateRequestQueue = ($, statesArray, requestQueue, branchesUrl) => {
  // get the list of state abbreviations from dropdown
  const $select = $('select#stval');
  if ($select) {
    $select.children('option').each((index, optionEl) => {
      const optionVal = $(optionEl).attr('value');
      if (optionVal) {
        statesArray.push(optionVal);
      }
    });
  }
  console.log('Got states array', statesArray);
  // enqueue a request for each state page
  statesArray.forEach(state => {
    requestQueue.addRequest({ url: `${branchesUrl}?stval=${state}&Select=Select` });
  });
}

(async () => {

  const branchesUrl = 'https://alliedbuilding.com/About/AlliedBranches';
  const states = [];
  const locationTemplate = {
    locator_domain: 'alliedbuilding.com',
    location_name: null,
    street_address: null,
    city: null,
    state: null,
    zip: null,
    country_code: '<MISSING>',
    store_number: '<MISSING>',
    phone: null,
    fax: null,
    location_type: '<MISSING>',
    latitude: null,
    longitude: null,
    hours_of_operation: null,
    receiving_hours: null
  };

  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ url: branchesUrl });

  const handlePageFunction = async ({ request, response, html, $ }) => {

    if (states.length === 0) {
      populateRequestQueue($, states, requestQueue, branchesUrl);
    }

    if(request.url === branchesUrl) {
      // on the initial request we'll grab the corp office info
      const corporateOffice = await parseCorporateOffice($, locationTemplate);
      if (corporateOffice) {
        await Apify.pushData(corporateOffice);
      }
      await log(request.url, [corporateOffice]);
    } else {
      // for all other requests we'll grab all the locations on the page
      const locations = await parseLocations($, locationTemplate);
      if (locations.length > 0) {
        await Apify.pushData(locations);
      }
      await log(request.url, locations);
    }
  
    await sleep();

  };

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    handlePageFunction,
  });

  await crawler.run();
})();
