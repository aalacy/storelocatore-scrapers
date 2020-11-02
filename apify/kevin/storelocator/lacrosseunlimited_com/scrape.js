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

const getHours = ($) => {
  let hours = '';
  $('.open')
    .each((i, hoursBlock) => {
      // heading for this hours block
      hours += $(hoursBlock).find('h2').eq(0).text().trim() + ' - ';
      // days and hours ...
      $(hoursBlock).find('td').each((j, td) => {
        const tdText = $(td).text().trim();
        if (tdText.includes('pm') || tdText.toLowerCase().includes('closed')) {
          hours += tdText + ', ';
        } else {
          hours += tdText + ' ';
        }
      });
    });
  return hours;
}

const parseLocation = async ($) => {
  const location = {
    locator_domain: 'lacrosseunlimited.com',
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
    hours_of_operation: null
  };

  location.location_name = $('h1.page-title').text().trim();

  const $addressBlock = $('div.main p.store-info:first-child span');

  $addressBlockTextNodes = 
    $addressBlock
      .contents()
      .filter(function() {
        return this.type === 'text'
      });

  location.phone = $addressBlockTextNodes.eq($addressBlockTextNodes.length-1).text().trim();

  const cityStateZip = $addressBlockTextNodes.eq($addressBlockTextNodes.length-2).text().trim();
  Object.assign(location, parseCityStateZip(cityStateZip));

  let streetAddress = '';
  $addressBlockTextNodes.each((i, elem) => {
    const text = $(elem).text().trim();
    if (i < $addressBlockTextNodes.length-2) {
      streetAddress = (streetAddress.length === 0) 
        ? text 
        : `${streetAddress}, ${text}`;
    }
  })
  location.street_address = streetAddress;

  // look through all the script blocks to find lat/lng
  $('script')
    .each((index, scriptBlock) => {
      const scriptContent = $(scriptBlock).text();
      const match = scriptContent.match(/{lat:([\d.-]+),lng:([\d.-]+),/);
      if (match) {
        location.latitude = match[1].trim();
        location.longitude = match[2].trim();
      }
    });

  location.hours_of_operation = getHours($);

  return location;
};

(async () => {

  const locationsUrl = 'https://lacrosseunlimited.com/store-locator';
  const userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' + 
    ' Chrome/75.0.3770.100 Safari/537.36'
  
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ 
    url: locationsUrl, 
    headers: {
      'user-agent': userAgent
    }
  });

  const handlePageFunction = async ({ request, response, html, $ }) => {

    console.log(`Got ${request.url}`);

    if (request.userData.isLocationPage) {

      const poi = await parseLocation($);
      console.log(poi);
      await Apify.pushData(poi);
      await sleep();

    } else {

      $('.tag-content a.view-detail').each((i, elem) => {
        const locUrl = $(elem).attr('href');
        requestQueue.addRequest({ 
          url: locUrl, 
          headers: {
            'user-agent': userAgent
          }, 
          userData: {
            isLocationPage: true
          }
        });
      });
      
      await sleep();

    }

  };

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    handlePageFunction,
  });

  await crawler.run();
})();
