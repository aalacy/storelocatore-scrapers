const url = require('url');
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

const parseLocation = async $ => {
  const poi = {
    locator_domain: 'lvac.com',
    location_name: null,
    street_address: null,
    city: null,
    state: null,
    zip: null,
    country_code: '<MISSING>',
    store_number: '<MISSING>',
    phone: null,
    location_type: '<MISSING>',
    latitude: null,
    longitude: null,
    hours_of_operation: '',
  }; 

  poi.location_name = $('.location-name span').text();

  const $address = $('address').eq(0);
  const $addressSpans = $address.find('span');
  poi.street_address = $addressSpans.eq(0).text().trim();
  poi.city = $addressSpans.eq(1).text().trim();
  poi.state = $addressSpans.eq(2).text().trim();
  poi.zip = $addressSpans.eq(3).text().trim();

  poi.phone = $('a.phone-cta-bottom').eq(0).text().trim();

  $('time')
    .eq(0)
    .contents()
    .filter(function() {
      return this.type === 'text'; 
    })
    .each((i, textNode) => {
      const text = $(textNode).text().trim();
      poi.hours_of_operation += 
        (poi.hours_of_operation.length === 0)
          ? text
          : ', ' + text

    });

  const $schemaScript = $('script[type="application/ld+json"]').eq(1);
  const schemaObj = JSON.parse($schemaScript.text().trim());
  poi.latitude = schemaObj.geo.latitude;
  poi.longitude = schemaObj.geo.longitude;

  return poi;
};


(async () => {
  const initialUrl = 'https://www.lvac.com/locations/';

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

  const handlePageFunction = async ({ request, response, html, $ }) => {

    console.log(`Got ${request.url}`);

    if (request.userData.isLocationDetailPage) {

      const poi = await parseLocation($);
      console.log(poi);

      await Apify.pushData(poi);
      await sleep();

    } else {

      $('.loc').each((index, div) => {

        const detailUrl = $(div).find('a').eq(0).attr('href');
        const fullUrl = url.resolve(request.loadedUrl, detailUrl);

        requestQueue.addRequest({
          url: fullUrl,
          headers: {
            'user-agent': userAgent
          },
          userData: {
            isLocationDetailPage: true
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
