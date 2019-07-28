const Apify = require('apify');
const {
  utils: { enqueueLinks },
} = Apify;

const userAgent =
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' +
    ' Chrome/75.0.3770.100 Safari/537.36';

function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}
const sleep = async () => {
  const ms = randomIntFromInterval(1000, 5000);
  console.log('sleeping ' + ms + 'ms');
  return Apify.utils.sleep(ms);
};

const getHours = $ => {
  let hours = '';
  $hoursP = $(".col1 > h2:contains('Hours')").next();

  $hoursP
    .eq(0)
    .contents()
    .filter(function() {
      return this.type === 'text';
    })
    .each((index, node) => {
      const nodeText = $(node)
        .text()
        .trim();
      hours += hours.length === 0 ? nodeText : ', ' + nodeText;
    });

  return hours;
};

const getPhone = $ =>
  $('a.telephone')
    .contents()
    .filter(function() {
      return this.type === 'text';
    })
    .text()
    .trim();

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

const getOrderPageDetails = async ($, poi) => {

  const newPoi = Object.assign({}, poi);

  $('span.footer')
    .contents()
    .filter(function() {
      return this.type === 'text'
    })
    .each((index, textNode) => {
      const textContent = $(textNode).text().trim();
      switch(index) {
        case 1: 
          newPoi.street_address = textContent
          break;
        case 2: 
          const cityStateZip = textContent;
          Object.assign(newPoi, parseCityStateZip(cityStateZip));
          break;
        
      }
    })

  return newPoi;
};

const parseDetailPage1 = async ($, locationName, requestQueue) => {
  const poi = {
    locator_domain: 'schnippers.com',
    location_name: null,
    street_address: null,
    city: '<MISSING>',
    state: '<MISSING>',
    zip: '<MISSING>',
    country_code: '<MISSING>',
    store_number: '<MISSING>',
    phone: getPhone($),
    location_type: '<MISSING>',
    latitude: '<MISSING>',
    longitude: '<MISSING>',
    hours_of_operation: getHours($),
  };

  poi.location_name = locationName;

  const orderPageUrl = $('.order-button')
    .eq(1)
    .attr('href');

   const match = orderPageUrl.match(/\/store(\d+)\//);
   if (match) {
     poi.store_number = match[1];
   }

  requestQueue.addRequest({
    url: orderPageUrl,
    headers: {
      'user-agent': userAgent,
    },
    userData: {
      pageType: 'order',
      poi: poi,
    },
  });

  return poi;
};

const getLocationName = $a => {
  const fullName = $a.text().trim();
  const neighborhood = $a
    .find('span.neighborhood')
    .eq(0)
    .text()
    .trim();
  return fullName.replace(neighborhood, `${neighborhood} -`);
};

(async () => {
  const initialUrl = 'http://www.schnippers.com/';

  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: initialUrl,
    headers: {
      'user-agent': userAgent,
    },
  });

  const handlePageFunction = async ({ request, response, html, $ }) => {
    console.log(`Got ${request.url}`);

    switch (request.userData.pageType) {
      case 'detail':

        await parseDetailPage1($, request.userData.location_name, requestQueue);
        break;

      case 'order':

        const poi = await getOrderPageDetails($, request.userData.poi);
        console.log(poi);

        await Apify.pushData(poi);
        await sleep();

        break;

      default:

        $('nav#restaurants li a').each((index, a) => {
          $a = $(a);
          const detailUrl = $a.attr('href');

          requestQueue.addRequest({
            url: detailUrl,
            headers: {
              'user-agent': userAgent,
            },
            userData: {
              pageType: 'detail',
              location_name: getLocationName($a),
            },
          });
        });

        await sleep();
        break;
    }
  };

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    handlePageFunction
  });

  await crawler.run();
})();
