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
  const $ = cheerio.load(await request.get('http://supermercadomitierra.com/locations.html'))

  $('#content .wrapper > div > div').each((_, storeElement) => {
    const contentBlock = $('div > p', storeElement);
    if (contentBlock.length > 0) {
      const matches = contentBlock.text().trim().match(
        /^[\s\n\t]*(?<location_name>[^\t\n]+)[\n\t\s]+(?<street_address>[^\t\n]+)[\n\t\s]+(?<city>.+),?\s(?<state>[A-Z]{2}),?\s(?<zip>[\d-]{5,10})[\s\n\t]+TEL:\s?(?<phone>[\(\)\d-\.\s]+)[\s\n\t]*$/
      ).groups;
      const { location_name, street_address, city, state, zip, phone } = matches;
      records.push({
        locator_domain: 'supermercadomitierra.com',
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
        hours_of_operation: '<MISSING>',
      })
    }
  })

	return records;

	// End scraper

}
