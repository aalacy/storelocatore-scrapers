const Apify = require('apify');
const {
  utils: { enqueueLinks },
} = Apify;

function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}

const sleep = async (min, max) => {
  const ms = randomIntFromInterval(min, max);
  console.log('sleeping ' + ms + 'ms');
  return Apify.utils.sleep(ms);
};

const parseCityStateZip = str => {
  // console.log('>>> parsing city state zip for >>>' + str + '<<<' )
  const returnObj = {
    city: null,
    state: null,
    zip: null,
  };
  const match = str.match(/^(.+),\s+?(\w{2})\s*(\w{3} \w{3})?/);
  if (match) {
    returnObj.city = match[1].trim();
    returnObj.state = match[2].trim();
    // a lot of locations are missing the zip code
    returnObj.zip = match[3] ? match[3].trim() : '<MISSING>';
  }
  //console.log('>>> return from parsing city state zip >>>', returnObj);
  return returnObj;
};

const isPhone = (strPhone) => {
  // replace anything that's not a digit
  strPhone = strPhone.replace(/\D/g, ''); 
  return strPhone.length === 10;
}

const isHours = str => /\d+.*am|\d+.*pm/.test(str.toLowerCase());

const parseLocation = (store, $) => {
  const loc = {
    locator_domain: 'lawtons.ca',
    location_name: store.title,
    street_address: null,
    city: null,
    state: null,
    zip: '<MISSING>',
    country_code: '<MISSING>',
    store_number: null,
    phone: '<MISSING>',
    location_type: '<MISSING>',
    latitude: store.latitude || '<MISSING>',
    longitude: store.longitude || '<MISSING>',
    hours_of_operation: '',
  };
  
  //console.log('store.categories', store.categories);
  loc.location_type = 
    store.categories.reduce((prev, current) => {
      return prev.length > 0 
        ? prev + ', ' + current.title 
        : current.title; 
    }, '');


  const storeNumberMatch = store.cssClass.match(/loc-(\d+)/);
  if (storeNumberMatch) {
    loc.store_number = storeNumberMatch[1];
  }

  descriptionDomNodes = $.parseHTML(store.description);
  const $addressPhoneHoursPs = $(descriptionDomNodes)
    .find('.address')
    .children('p');

  // address is in the first <p>
  const $addressTextNodes = $addressPhoneHoursPs
    .eq(0)
    .contents()
    .filter(function() {
      return this.type === 'text';
    });

  loc.street_address = $addressTextNodes.eq(0).text().trim();

  const cityStateZip = $addressTextNodes.eq(1).text().trim();
  Object.assign(loc, parseCityStateZip(cityStateZip));

  // loop through the rest of the <p> tags 
  $addressPhoneHoursPs.each((index, p) => {
    $(p)
      .contents()
      .filter(function() {
        return this.type === 'text';
      })
      .each((i, textNode) => {
        const text = $(textNode).text();
        //console.log('>>> text ', text);
        if (isPhone(text)) {
          loc.phone = text;
        } else if (isHours(text)) {
          loc.hours_of_operation += text;
        } 
      });
  });

  return loc;
};

const getStoresArray = $ => {
  let $storesScript = $('script:not([src])');

  let scriptContent = $storesScript
    .filter((index, elem) => {
      return $(elem)
        .text()
        .includes('KOObject');
    })
    .eq(0)
    .text();

  // parse out the object literal, throwing away other js outside of it
  const match = scriptContent.match(/({.+})/);
  if (match) {
    scriptContent = match[1];
  }

  const obj = JSON.parse(scriptContent);
  const storesArray = obj.KOObject[0].locations;

  return storesArray;
};

(async () => {
  const initialUrl = 'https://lawtons.ca/stores/';

  const userAgent =
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' +
    ' Chrome/75.0.3770.100 Safari/537.36';

  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: initialUrl,
    headers: {
      'user-agent': userAgent,
    },
  });

  const handlePageFunction = async ({ request, response, html, $ }) => {

    console.log(`Got ${request.url}`);

    const storesArray = getStoresArray($);
    console.log(storesArray);
    console.log(`>>> found ${storesArray.length} total locations
    
    `);

    storesArray.forEach(async store => {
      const loc = parseLocation(store, $);
      console.log(loc);
      await Apify.pushData(loc);
    });
  };

  const handleFailedRequestFunction = async () => {
    // the initial page is prone to returning 502 error if it's hit too often. 
    // if it doesn't return status 200 the first time, wait a bit before trying again. 
    if (response.statusCode != 200) {
      await sleep(10000, 60000);
    }
  }

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    handlePageFunction,
    maxConcurrency: 1
  });

  await crawler.run();
})();
