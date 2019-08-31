const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');


Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const records = [];
  const $  = cheerio.load(await request.get('https://www.phoenixmovies.net'));
  $('.text10[valign="top"]').each((_, poiElement) => {
    // get rid of excess stuff
    $('div:first-child', poiElement).remove();
    // get latitude and longitude from directions link, if it exists
    let latitude, longitude;
    const latLong = $('a', poiElement).last().attr('href').match(/(\&sll\=|@)(?<latitude>-?\d{1,3}\.\d*),(?<longitude>-?\d{1,3}\.\d*)/)
    if (!!latLong) {
      ({ latitude, longitude } = latLong.groups);
    }
    let { street_address, city, state, zip, phone } = $(poiElement).text().trim().match(
      /(?<street_address>[\.A-Za-z\d\s]*)\s*\n\s*(?<city>[A-Za-z ]+),? (?<state>[A-Z]{2}) (?<zip>[\d-]{5,10})\s*\n\s*[\d\D]*Customer Service Line:\s+(?<phone>[\(\)\d- \.]*)/
    ).groups;
    street_address = street_address.replace(/\s/, ' ');
    const location_name = $(poiElement).parent().prev().text().trim();
    records.push({
      locator_domain: 'phoenixmovies.net',
      location_name,
      street_address,
      city,
      state,
      zip,
      country_code: '<MISSING>',
      store_number: '<MISSING>',
      phone,
      location_type: '<MISSING>',
      latitude: latitude || '<MISSING>',
      longitude: longitude || '<MISSING>',
      hours_of_operation: '<MISSING>'
    })
  })

	return records;

	// End scraper

}
