const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const rootAddress = new URL('http://www.brandonsdiner.com/locations/');
  const $ = cheerio.load(await request.get(rootAddress.href));
  records = [];

  const poiElements = $('.entry-content .et_pb_row .et_pb_column_1_3:first-child .et_pb_text').get();
  const coordinates = $('.entry-content .et_pb_row .et_pb_column_1_3:nth-child(3) .et_pb_text').map((_, element) => {
    const iframeSrc = $('iframe', element).attr('src');
    return {latitude, longitude} = iframeSrc.match(/!2d(?<longitude>-?[\d\.]*)!3d(?<latitude>-?[\d\.]*)!/).groups
  }).get()

  for (let index = 0; index < poiElements.length; index++) {
    const element = poiElements[index];
    const nameElement = $('h2,h3', element);
    const {street_address, city, state, zip, phone} = nameElement.next('p').text().trim().match(
      /(?<street_address>.*)\s*\n(?<city>[a-zA-Z\s]*),\s(?<state>[A-Z]{2})\s(?<zip>[\d-]*)\s*\n(?<phone>[\(\)\d\s-\.]*)/
    ).groups;
    records.push({
      locator_domain: 'brandonsdiner.com',
      location_name: nameElement.text(),
      street_address,
      city,
      state,
      zip,
      country_code: 'US',
      store_number: '<MISSING>',
      phone,
      location_type: '<MISSING>',
      latitude: coordinates[index].latitude,
      longitude: coordinates[index].longitude,
      hours_of_operation: '<MISSING>',
    }
    )
  }

	return records;

	// End scraper

}
