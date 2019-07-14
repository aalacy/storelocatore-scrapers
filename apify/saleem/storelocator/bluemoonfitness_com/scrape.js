const Apify = require('apify')
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  var records = [];
  await request('https://www.bluemoonfitness.com/gym-locations/', function (error, response, html) {
    if (!error && response.statusCode == 200) {
      var $ = cheerio.load(html);

      // location information is in individual list elements
      $('.loc-list').find('li').each((index, location_element) => {

        const rawAddress = $('.info', location_element).text();
        const {groups: addressParts} = rawAddress.match(/\s*(?<street_address>.+)\n\s*(?<city>.+),\s*(?<state>[A-Z]{2})\s*(?<zip>\d+)[\n.\s]*(?<phone>.*?)[\n\s]*$/);

        const directionsLink = $('a:contains(Get Directions)', location_element).attr('href');
        const {groups: {lat, long}} = directionsLink.match(/\@(?<lat>[-?\d\.]*)\,(?<long>[-?\d\.]*)/);

        records.push({
          locator_domain: 'bluemoonfitness.com',
          location_name: $('h3', location_element).text().trim(),
          street_address: addressParts.street_address,
          city: addressParts.city,
          state: addressParts.state,
          zip: addressParts.zip,
          country_code: 'US',
          store_number: '<MISSING>',
          phone: addressParts.phone,
          location_type: '<MISSING>',
          latitude: lat,
          longitude: long,
          hours_of_operation: '<MISSING>',
        });
      });
    }
    else {
      throw 'Invalid response from address.'
    }
  });
  return records;
	// End scraper

}
