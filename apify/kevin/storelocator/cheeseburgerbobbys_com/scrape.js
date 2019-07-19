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

const parseLocation = async ($) => {
  const location = {
    locator_domain: 'cheeseburgerbobbys.com',
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

  $locationDiv = $('div.page-content');
  
  location.location_name = $locationDiv.children('h2').eq(0).text();

  const $childPs = $locationDiv.children('p').not('#subtitle');

  const $addressP = $childPs.eq(0);

  const $addressAndPhoneTextNodes = 
      $addressP
        .contents()
        .filter(function() {
          return this.type === 'text'; 
        });

  // first text node should be the street address...
  location.street_address = $addressAndPhoneTextNodes.eq(0).text().trim();

  const cityStateZip = $addressAndPhoneTextNodes.eq(1).text().trim();

  const match = cityStateZip.match(/^(.+?), (.+?)(?=$| (\d{5}))/);
  if (match) {
    location.city = match[1].trim();
    location.state = match[2].trim();
    location.zip = match[3] ? match[3].trim() : '<MISSING>';
  }

  location.phone = $addressAndPhoneTextNodes.eq(2).text().trim();

  const $hoursP = $childPs.eq(1);
  const $hoursTextNodes = 
      $hoursP
        .contents()
        .filter(function() {
          return this.type === 'text'; 
        });

  location.hours_of_operation = 
    `${$hoursTextNodes.eq(1).text().trim()}, ${$hoursTextNodes.eq(2).text().trim()}`;

  return location;
};

(async () => {

  const locationsUrl = 'https://cheeseburgerbobbys.com/locations/';
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

    if (request.userData.isLocationPage) {

      console.log(`Got ${request.url}`);
      const location = await parseLocation($);
      await Apify.pushData(location);
      await sleep();

    } else {

      $('li.submenu_link a').each((i, elem) => {
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
