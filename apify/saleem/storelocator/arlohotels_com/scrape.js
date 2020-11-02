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
  const $ = cheerio.load(await request.get('https://www.arlohotels.com'));
  $('.footer__hotel-container').children().each((_, element) => {
    const location_name = $('.address__hotel-name', element).text().trim();
    const { street_address, city, state, zip } = $('p a', element).eq(0).text().trim().match(
      /^(?<street_address>.*)\s*?\n\s*?(?<city>.*), (?<state>[A-Z]{2}) (?<zip>[\d-]*?)$/
    ).groups;
    const phone = $('p a', element).eq(1).text();
    records.push({
      locator_domain: 'arlohotels.com',
      location_name,
      street_address,
      city,
      state,
      zip,
      country_code: 'US',
      store_number: '<MISSING>',
      phone,
      location_type: '<MISSING>',
      latitude: '<MISSING>',
      longitude: '<MISSING>',
      hours_of_operation: '<MISSING>'})
  })
	return records;

	// End scraper

}
