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
  await request('https://blackstonesteakhouse.com/locations/')
    .then(async function (html) {
      var $ = cheerio.load(html);
      
      // NOTES:
      // individual locations are encapsulated in .et_pb_text1, .et_pb_text2, etc.
      // third location appears to have been added later and does not match conventions with other locations
      // it's Directions link is also minified so does not contain latitude/longitude data
      var location_index = 1;
      var location_element;
      while ((location_element = $(`.et_pb_text_${location_index}`)).length > 0) {
        if (location_element.length > 1 ) {
          throw 'Website has changed, rendering scraper obsolete. Selected element is not unique.'
        }

        const rawAddress = $('li', location_element).text();
        const {groups: addressParts} = rawAddress.match(/(?<street_address>.+)\n(?<city>.+),\s(?<state>[A-Z]{2})\s(?<zip>\d+)\n.*\s(?<phone>\D?(\d{3})\D?\D?(\d{3})\D?(\d{4}))/);

        const directionsLink = $('a:contains(Directions)', location_element).attr('href');
        const {groups: {lat, long}} = directionsLink.match(/\@(?<lat>[-?\d\.]*)\,(?<long>[-?\d\.]*)/) || {groups:{lat:'<MISSING>', long:'<MISSING>'}};

        records.push({
          locator_domain: 'blackstonesteakhouse.com',
          location_name: $('h2', location_element).text(),
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
        
        location_index++;
      }
    });
  return records;
	// End scraper

}
