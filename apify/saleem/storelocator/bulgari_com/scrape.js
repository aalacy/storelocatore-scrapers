const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

(async () => {
  // Two pages contains links and some data to all the stores in those countries
  const sources = [
    { url: 'https://www.bulgari.com/en-us/storelocator/canada' },
    { url: 'https://www.bulgari.com/en-us/storelocator/united+states' }
  ];

  const storeList = [];
  
  for (const source of sources) {
    await request.get(source.url)
    .then(html => {
      const $ = cheerio.load(html);
      JSON.parse($('.map-canvas').attr('data-locations')).forEach( location => {
        storeList.push({
          url: `https://www.bulgari.com/en-us/storelocator/${location.storeCountry}/${location.storeCity}/${location.storeNameUrl}-${location.storeId}`,
          userData: location
        })
      })
    })
    .catch(error =>{
      throw `Error get list of store pages: ${error}`
    })
  };

  const storeRequestList = new Apify.RequestList({sources: storeList});
  await storeRequestList.initialize();

  const records = []

  const storeCrawler = new Apify.CheerioCrawler({
    requestList: storeRequestList,
    handlePageFunction: async ({ request, response, html, $ }) => {
      const addressText = $('.storelocator-bread-subtitle').text();
      let addressParts={}
      try {
        addressParts = addressText.match(/[\d\D]*\n+?\s*(?<city>.*),\s*\n+?\s*(?<state>.*)\s*\n+?\s*(?<zip>.*)\s*\n*?$/).groups;
      } catch (error) {
        console.log(`Couldn't parse address: ${addressText} at URL: ${request.url}, failed with error: ${error}`)
      }
      records.push({
        locator_domain: 'bulgari.com',
        location_name: $('.storelocator-bread-title').text(),
        raw_address: addressText.replace(/\n/g, ' ').trim(),
        // The street address first line sometimes includes the city and state, so can't
        // guarantee it will always be just street_address. e.g.: https://www.bulgari.com/en-us/storelocator/united+states/greenwich/saks+fifth+avenue-1115
        street_address: '<INACCESSIBLE>',
        city: addressParts.city || '<INACCESSIBLE>',
        state: addressParts.state || '<INACCESSIBLE>',
        zip: addressParts.zip || '<INACCESSIBLE>',
        country_code: $('.info-locator-country').text(),
        store_number: request.userData.storeId,
        phone: request.userData.storePhone || '<MISSING>',
        // There's also a storeType field, but that is just a number so I'm using the more
        // descriptive option
        location_type: request.userData.itemSubtitle,
        latitude: request.userData.latitude,
        longitude: request.userData.longitude,
        hours_of_operation: $('.store-hours').text().replace(/\s+/g, ' ')
      });
    }
  });

  await storeCrawler.run();
  await Apify.pushData(records);
  
  // End scraper
})();
