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
  const $ = cheerio.load(await request.get({
    url: 'https://www.allindia.cafe',
    headers: {
      'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15'
    }
  }));

  // most semantic way to locate the location info on page is in the section with id location-page,
  // look for the map-block's then navigate from there to the corresponding text
  $('#location-page .map-block').each((_, element) => {
    const { location_name, street_address, city, state, zip, phone, hours_of_operation } = $(element).parent().prev().text().trim().match(
      /^(?<location_name>[A-Z]*)\s*(?<street_address>\d[\d A-Za-z\.]*)\s*?(?<city>[A-Z][a-zA-Z]*?)\b,?\s*?\b(?<state>[A-Z]{2})\b\s*?\b(?<zip>[\d-]{5,10})\s*?(?<phone>\([\)\d -]{10,})\s*?HOURS\s*?(?<hours_of_operation>.*?)$/
    ).groups
    const { markerLat: latitude, markerLng: longitude }= JSON.parse($(element).attr('data-block-json')).location;
    records.push({
      locator_domain: 'allindia.cafe',
      location_name,
      street_address,
      city,
      state,
      zip,
      country_code: 'US',
      store_number: '<MISSING>',
      phone,
      location_type: '<MISSING>',
      latitude,
      longitude,
      hours_of_operation,
    })
  })

	return records;

	// End scraper

}
