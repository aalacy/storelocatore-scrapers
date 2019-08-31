const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const records = []
  const $ = cheerio.load(await request.get('http://kwikking.com/locations.php'));
  
  // all of the location data is in these .style1 sections
  $('.style1').each((_, section) => {
    // for each section, get an array of direction links to scrape lat/long from
    const directionLinks = $('a[target="_blank"]', section).map((_, element) => {
      return $(element).attr('href')
    })

    let match = []
    const regex = /\s*(?<city_location>.+?)( Location:)?\s*(?<street_address>\d.+)\s*((?<city>[A-Za-z ]+), (?<state>[A-Za-z ]+)(?<zip>[\d-]+)\s*)?Phone:(?<phone>[\(\)\d -]+)([\s.]*.*\s*(?<hasDirections>[cC]lick))?/g;
    let sectionText = $(section).text().trim();
    // search sectionText for as many poi's as it contains and get data for each
    while (match = regex.exec(sectionText)) {
      let city, state, street_address, zip, country_code, latitude, longitude
      // if poi match has a directionLink (/Click for directions/ was found in its text), get data from it
      if (!!match.groups.hasDirections) {
        ({ city, state, street_address, zip, country_code, latitude, longitude } = directionLinks.splice(0,1)[0].match(
          /city\=(?<city>.*)\&state\=(?<state>.*)\&address\=(?<street_address>.*)\&zipcode\=(?<zip>.*)\&country\=(?<country_code>.*)\&latitude\=(?<latitude>.*)\&longitude\=(?<longitude>.*?)&/
          ).groups);
        street_address = street_address.replace(/\+/g, ' ');
      // otherwise, no way to get lat and long
      } else {
        latitude = '<MISSING>', longitude = '<MISSING>'
      }
      records.push({
        locator_domain: 'kwikking.com',
        location_name: match.groups.city_location || '<MISSING>',
        street_address: street_address || match.groups.street_address || '<MISSING>',
        city: city || match.groups.city || match.groups.city_location || '<MISSING>',
        state: state || match.groups.state || '<MISSING>',
        zip: zip || match.groups.zip || '<MISSING>',
        country_code: country_code || '<MISSING>',
        store_number: '<MISSING>',
        phone: match.groups.phone,
        location_type: '<MISSING>',
        latitude,
        longitude,
        hours_of_operation: '<MISSING>'
      })
    }

  });

	return records;

	// End scraper

}
