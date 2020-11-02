const Apify = require('apify');
const {
  utils: { enqueueLinks },
} = Apify;

const parseCityStateZip = str => {
  const returnObj = {
    city: null,
    state: null,
    zip: null,
  };
  const match = str.match(/^(.+),\s+?(\w{2})\s+?(\d{5}(-\d{4})?)/);
  if (match) {
    returnObj.city = match[1].trim();
    returnObj.state = match[2].trim();
    returnObj.zip = match[3].trim();
  }
  return returnObj;
};

const parseLocation = (div, $, storesArray) => {
  
  const loc = {
    locator_domain: 'lassus.com',
    location_name: null,
    street_address: null,
    city: null,
    state: null,
    zip: null,
    country_code: '<MISSING>',
    store_number: null,
    phone: null,
    location_type: '<MISSING>',
    latitude: '<MISSING>',
    longitude: '<MISSING>',
    hours_of_operation: null,
  };

  const $div = $(div);

  const locationTitle = $div
    .find('h4.modal-title')
    .text()
    .trim();
  const shortAddress = $div
    .find('h4.location-link')
    .text()
    .trim();

  loc.location_name = `${locationTitle} - ${shortAddress};`;

  loc.store_number = locationTitle.match(/#(\d+)$/)[1].trim();

  $addressAndPhone = $div
    .find('div.modal-body > div.row > div')
    .eq(1)
    .find('p')
    .eq(0);

  $addressAndPhoneTextNodes = 
    $addressAndPhone
      .contents()
      .filter(function() {
        return this.type === 'text'; 
      });

  loc.street_address = $addressAndPhoneTextNodes.eq(0).text().trim();

  const cityStateZip = $addressAndPhoneTextNodes.eq(1).text().trim();
  Object.assign(loc, parseCityStateZip(cityStateZip));

  loc.phone = $addressAndPhoneTextNodes.eq(2).text().trim();

  const storeObj = storesArray.find(store => store.store_number === loc.store_number);
  loc.latitude = storeObj.latitude;
  loc.longitude = storeObj.longitude;

  $hours = $div
    .find('div.modal-body > div.row > div')
    .eq(2)
    .find('p');

  loc.hours_of_operation = '';
  $hours
    .each((i, p) => {
      $(p)
        .contents()
        .filter(function() {
          return this.name != 'br'; 
        })
        .each((j, n) => {
          if (n.name === 'strong') {

            const heading = $(n).text().trim();
    
            loc.hours_of_operation += 
              loc.hours_of_operation.length === 0 
                ? heading + ' '
                : '; ' + heading + ' ';

          } else if (n.type === 'text') {

            let theText = $(n).text().trim();

            // remove phone number if present
            theText = theText.replace(/ \| Phone:.+$/, '');

            loc.hours_of_operation += theText;
          }
        })
    });

  return loc;
};

(async () => {
  const initialUrl = 'https://www.lassus.com/lassus-locations/';

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

    let storesScript = $('div#body-content').next('script').text().trim();
    storesScript = storesScript.replace('var stores = ', '');
    const storesArray = JSON.parse(storesScript);

    const $locationDivs = $('div.single-location');

    console.log(`>>> found ${$locationDivs.length} total locations`);

    $locationDivs.each(async (i, div) => {
      
      const loc = parseLocation(div, $, storesArray);
      console.log(loc.location_name);
      await Apify.pushData(loc);

    });
  };

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    handlePageFunction,
  });

  await crawler.run();
})();
