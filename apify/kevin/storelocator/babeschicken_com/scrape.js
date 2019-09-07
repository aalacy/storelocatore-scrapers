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

const parseCityStateZip = (cityStateZipString) => {
  const obj = {};
  const match = cityStateZipString.match(/^(.+?),(.+?) (\d{5})/);
  if (match) {
    obj.city = match[1].trim();
    obj.state = match[2].trim();
    obj.zip = match[3].trim();
  }
  return obj;
}

const parseLatLong = (googleMapsUrl) => {
  const obj = {};
  const match = googleMapsUrl.match(/sll=([\d.-]+),([\d.-]+)&/);
  if (match) {
    obj.latitude = match[1].trim();
    obj.longitude = match[2].trim();
  }
  return obj;
}

const parseLocation = async ($) => {
  const location = {
    locator_domain: 'babeschicken.com',
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

  location.location_name = $('a[aria-current]').eq(0).text();

  $locationDiv = $('#location-info');

  $addressAndPhoneUl = $locationDiv.children('ul').eq(2);
  $addressAndPhoneUl.children('li').each((index, li) => {
    switch (index) {
      case 0: 
        location.street_address = $(li).text();
        break;
      case 1: 
        const cityStateZip = $(li).text();
        Object.assign(location, parseCityStateZip(cityStateZip));
        
        // the lat long values from the maps url aren't correct. we'll set to <MISSING> instead.
        //Object.assign(location, parseLatLong($(li).find('a').attr('href')));
        break;
      case 2: 
        location.phone = $(li).text().replace('tel. ', '');
        break;
    }

    let hours = '';

    $hoursWeekdays = $locationDiv.children('ul').eq(3).children('li');
    hours += $hoursWeekdays.eq(0).text();
    hours += ": ";
    hours += $hoursWeekdays.eq(1).text();
    hours += " | ";
    hours += $hoursWeekdays.eq(2).text();
    hours += " -- ";

    $hoursWeekends = $locationDiv.children('ul').eq(4).children('li');
    hours += $hoursWeekends.eq(0).text();
    hours += ": ";
    hours += $hoursWeekends.eq(1).text();

    location.hours_of_operation = hours;
    
  });

  return location;
};


(async () => {

  const branchesUrl = 'http://www.babeschicken.com/our-kitchens/';
  const userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' + 
    ' Chrome/75.0.3770.100 Safari/537.36'
  
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ 
    url: branchesUrl, 
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

      $('#locations-list li a').each((i, elem) => {
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
