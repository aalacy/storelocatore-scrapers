const Apify = require('apify')
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const records = [];
  await request('https://www.bluemoonfitness.com/gym-locations/')
    .then(async function (html) {
      let $ = cheerio.load(html);

      // location information is in individual list elements
      const locationList = $('.loc-list').find('li').toArray();
      for (const location_element of locationList) {
        // get address
        const rawAddress = $('.info', location_element).text();
        const {groups: addressParts} = rawAddress.match(/\s*(?<street_address>.+)\n\s*(?<city>.+),\s*(?<state>[A-Z]{2})\s*(?<zip>\d+)[\n.\s]*(?<phone>.*?)[\n\s]*$/);

        // get lat and long if available in directions link
        const directionsLink = $('a:contains(Get Directions)', location_element).attr('href');
        const {groups: {lat, long}} = directionsLink.match(/\@(?<lat>[-?\d\.]*)\,(?<long>[-?\d\.]*)/);

        // click on location info and get hours from indivual page
        const informationLink = $('a:contains(Location Info)', location_element).attr('href');
        var hours_of_operation;
        await request(informationLink)
          .then(function (html) {
            let $ = cheerio.load(html);
            hours_of_operation = $('.unit:contains(Hours)').find('.panel').text();
          })
          .catch(function () {
            throw "Couldn't load location information page to get Hours"
          });

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
          hours_of_operation: hours_of_operation,
        });

      };
    })
    .catch(function () {
      throw 'Invalid response from address.'
    });

  return records;
	// End scraper

}
