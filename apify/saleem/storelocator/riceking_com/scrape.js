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
  const $ = cheerio.load(await request.get('http://riceking.com/location.htm'))
  const regex = /\b(?<location_name>[A-Z a-z\d#\.\/\()\)-]*),?\s*?\b(?<street_address>[A-Z a-z\d#\.,-]*),?\s*?\n\s*?\b(?<city>[A-Z][A-Z a-z]*)\b,?\s*?(?<state>[A-Z]{2})\s*?\b(?<zip>[\d-]{5,10})\b\s*?\n(Tel:)?\s*?\b(?<phone>[\d-]{9,12})\b/g;
  let match = ''
  while (match = regex.exec($('body').text())) {
    match = match.groups;
    // some locations are single per city, named by city; others are multiple per city
    if (match.city_location !== match.city) {
      match.location_name = `${match.city}- ${match.location_name}`
    }
    records.push({
      locator_domain: 'riceking.com',
      location_name: match.location_name,
      street_address: match.street_address,
      city: match.city,
      state: match.state,
      zip: match.zip,
      country_code: 'US',
      store_number: '<MISSING>',
      phone: match.phone,
      location_type: '<MISSING>',
      latitude: '<MISSING>',
      longitude: '<MISSING>',
      hours_of_operation: '<MISSING>'
    })
  }

	return records;

	// End scraper

}
