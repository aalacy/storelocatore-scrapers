const Apify = require('apify');
const {
  utils: { enqueueLinks },
} = Apify;

const parseLocationData = async $ => {
  const store = {
    locator_domain: 'airheadsusa.com',
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

  store.location_name = $('.p1 b span').text();

  let $addressAndPhone =  $('.p1 > span');

  let cityStateZipText; 

  if ($addressAndPhone.length === 0) {

    // at the time of writing, the page for Pinellas location was missing the spans under .p1
    // so parse the child text nodes instead

    const $addressAndPhoneTextNodes = 
      $('.p1')
        .contents()
        .filter(function() {
          return this.type === 'text'; 
        });

    store.street_address = $addressAndPhoneTextNodes.eq(0).text().trim();
    
    cityStateZipText = $addressAndPhoneTextNodes.eq(1).text();

    store.phone = $addressAndPhoneTextNodes.eq(3).text().trim(); 

  } else {

    store.street_address = $addressAndPhone.eq(0).text().trim();

    cityStateZipText = $addressAndPhone.eq(1).text();

    store.phone = $addressAndPhone.eq(2).text();

  }

  const match = cityStateZipText.match(/^(.+?),(.+?) (\d{5})/);
  if (match) {
    store.city = match[1].trim();
    store.state = match[2].trim();
    store.zip = match[3].trim();
  }
  
  $hours = $('.p1').parent().parent().next('div');
  if ($hours.length) {
    store.hours_of_operation = $hours.text().trim();
  }
  
  return store;
};

(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://airheadsusa.com/',
    userData: {
      pageType: 'start',
    },
  });

  const handlePageFunction = async ({ request, response, html, $ }) => {

    if (request.userData.pageType === 'hours') {
      const locationData = await parseLocationData($);
      if (locationData != null) {
        await Apify.pushData(locationData);
      }
      return;
    }

    await enqueueLinks({
      $,
      requestQueue,
      pseudoUrls: [/^https:\/\/[\w-]+\.airheadsusa\.com\/$/],
      baseUrl: request.loadedUrl
    });

    await enqueueLinks({
      $,
      requestQueue,
      pseudoUrls: [/^https:\/\/[\w-]+\.airheadsusa\.com\/hours\/$/],
      baseUrl: request.loadedUrl,
      transformRequestFunction: function(request) {
        request.userData = { pageType: 'hours' };
        return request;
      }
    });

  };

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    handlePageFunction,
  });

  await crawler.run();
})();
