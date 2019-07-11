const Apify = require('apify');
const {
  utils: { enqueueLinks },
} = Apify;

const log = async (currentUrl, enqueued, locationData) => {
  const enqueuedUrls = enqueued.map(queueOpInfo => queueOpInfo.request.url);
  console.log('\n-----\n');
  console.log(`Got ${currentUrl}`);
  console.log(`Found ${enqueuedUrls.length} URLs`);
  console.log(enqueuedUrls);
  if (locationData) {
   console.log('Location data', locationData);
  }
};

function randomIntFromInterval(min,max) {
  // min and max included
  return Math.floor(Math.random()*(max-min+1)+min);
}

const sleep = async () => {
  const ms = randomIntFromInterval(1000, 5000)
  console.log('sleeping ' + ms + 'ms');
  return Apify.utils.sleep(ms);
}

const getHours = async ({$, hoursTitle}) => {
  let dataEl = null;
  $('.LocationInfo-hoursTitle').each((index, element) => {
    if ($(element).text() === hoursTitle) {
      dataEl = $(element)
        .parent('.LocationInfo-hoursHeader')
        .next('.LocationInfo-hoursTable')
        .find('.js-location-hours')
        .data('days');
      return false; // break out of `.each` loop
    }
  });
  return JSON.stringify(dataEl);
}

const parseLocationData = async ($, requestQueue) => {
  const locTemplate = {
    locator_domain: 'acmemarkets.com',
    location_name: null,
    street_address: null,
    city: null,
    state: null,
    zip: null,
    country_code: null,
    store_number: '<MISSING>',
    phone: null,
    location_type: null,
    latitude: null,
    longitude: null,
    hours_of_operation: null,
  };

  const $locationName = $('span.LocationName-geo');
  if ($locationName.length) {
    // we found a detail page

    const store = Object.assign({}, locTemplate);

    store.location_name = $locationName.text();
    store.location_type = 'Store';
    store.street_address = $('.LocationInfo-address .c-address-street-1').text();
    const address2 =  $('.LocationInfo-address .c-address-street-2').text();
    if (address2) {
      store.street_address += ', ' + address2;
    }
    store.city = $('.LocationInfo-address .c-address-city').text();
    store.state = $('.LocationInfo-address .c-address-state').text();
    store.zip = $('.LocationInfo-address .c-address-postal-code').text();
    store.country_code = $('.LocationInfo-address .c-address-country-name').text();
    store.phone = $('.LocationInfo-phones--store .c-phone-main-number-span').text();
    store.latitude = $('.coordinates meta[itemprop="latitude"]').attr('content');
    store.longitude = $('.coordinates meta[itemprop="longitude"]').attr('content');
    store.hours_of_operation = await getHours({$, hoursTitle: 'Store Hours'});

    // the site loads data for the pharmacy location via ajax...
    // we can call the same endpoint and use JSON.parse handlePageFunction. 

    // find the pharmacy ID
    const pharmacyId = $('.js-PharmacyData').data('pharmacy-id');
    if (pharmacyId) {
      // create a copy of the main store location object 
      const pharmacy =  Object.assign({}, store);
      pharmacy.location_type = 'Pharmacy';

      // enqueue the request and pass the pre-populated object to fill in with the pharmacy-specific fields
      await requestQueue.addRequest({
        url: `https://local.acmemarkets.com/pharmacydata/${pharmacyId.toLowerCase()}.html`,
        userData: {
          isPharmacyData: true,
          pharmacy
        }
      });
    }

    return store;
  }
  return null;
}

(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://local.acmemarkets.com/index.html'
  });

  const handlePageFunction = async ({ request, response, html, $ }) => {

    if (request.userData.isPharmacyData) {
      // grab the pre-populated pharmacy object attached to the request
      const locationData = request.userData.pharmacy;
      // this request returns json
      const pharmacyData = JSON.parse(html);
      locationData.phone = pharmacyData.phones[0].number;
      locationData.hours_of_operation = JSON.stringify(pharmacyData.hours);
      await Apify.pushData(locationData);
      await log(request.url, [], locationData);
      await sleep();
      return;
    }

    const enqueued = await enqueueLinks({
      $,
      requestQueue,
      selector: '.c-directory-list-content-item-link, .Teaser-nameLink',
      baseUrl: request.loadedUrl,
    });

    const locationData = await parseLocationData($, requestQueue);
    if (locationData != null) {
      await Apify.pushData(locationData);
    }

    await log(request.url, enqueued, locationData);
    await sleep();
    
  };

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    handlePageFunction,
  });

  await crawler.run();
})();
