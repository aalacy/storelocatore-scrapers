const Apify = require('apify');
const {
  utils: { enqueueLinks },
} = Apify;

function isPhone(strPhone) {
  strPhone = strPhone.trim();
  // replace anything that's not a digit
  strPhone = strPhone.replace(/\D/g, ''); 
  return strPhone.length === 10;
}

const parseLocationData = async $ => {
  const storeTemplate = {
    locator_domain: 'italianpie.com',
    location_name: null,
    street_address: null,
    city: '<MISSING>',
    state: '<MISSING>',
    zip: '<MISSING>',
    country_code: '<MISSING>',
    store_number: '<MISSING>',
    phone: '<MISSING>',
    location_type: '<MISSING>',
    latitude: '<MISSING>',
    longitude: '<MISSING>',
    hours_of_operation: '<MISSING>',
  };

  const locations = [];

  const $strongs = $('strong');
  $strongs.each((index, strongEl) => {

    // copy the template to a new location object
    const loc = Object.assign({}, storeTemplate);

    loc.location_name = $(strongEl).text().trim();

    // get the parent <p>, which is the container for everything else
    const $parentP = $(strongEl).parent('p');

    if (!$parentP) {
      return true; // continue to next iteration of each <strong> element
    }

    // if there's a previous sibling <h4> it might be the Corporate Office
    if ($parentP.prev('h4').text().toLowerCase() === 'corporate office') {
      loc.location_name = `Corporate Office - ${loc.location_name}`;
    }

    // not much markup, so look at the text nodes
    const $addressAndPhoneTextNodes = 
      $parentP
        .contents()
        .filter(function() {
          return this.type === 'text'; 
        });

    // first text node should be the street address...
    const street = $addressAndPhoneTextNodes.eq(0).text().trim();

    if ( !street ) {
      // no data for this location
      // continue to next iteration of each <strong> element
      return true; 
    }

    loc.street_address = street;
    
    // the next text node might be a phone, or it might be the city, state zip
    const phoneOrCityStateZip = $addressAndPhoneTextNodes.eq(1).text().trim();

    if (isPhone(phoneOrCityStateZip)) {
      loc.phone = phoneOrCityStateZip;
    } else {
      // not a phone, so parse the city, state, zip
      const match = phoneOrCityStateZip.match(/^(.+?),(.+?) (\d{5})/);
      if (match) {
        loc.city = match[1].trim();
        loc.state = match[2].trim();
        loc.zip = match[3].trim();
      }
      // check if there's a phone on the following line
      const maybePhone = $addressAndPhoneTextNodes.eq(2).text().trim();
      if (isPhone(maybePhone)) {
        loc.phone = maybePhone;
      }
    }

    // check for hours
    const $hours = $parentP.find('span.hours');

    if ($hours.length) {
      loc.hours_of_operation = $hours.text().trim();
    }

    locations.push(loc);

  });

  return locations;
};

(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'http://italianpie.com/italianpie-locations.htm'
  });

  const handlePageFunction = async ({ request, response, html, $ }) => {

    const locationData = await parseLocationData($);
    if (locationData != null) {
      await Apify.pushData(locationData);
    }

  };

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    handlePageFunction,
  });

  await crawler.run();
})();
