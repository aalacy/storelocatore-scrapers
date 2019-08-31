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
  const $ = cheerio.load(await request.get('https://www.althotels.com/en/'));

  $('.contact_wrapper .grid_item').each((_, store_element) => {
    const storeDetails = $('li', store_element);
    const { city, state, zip } = storeDetails.eq(2).text().trim().match(
      /^(?<city>.*)\b\s*?\(\s*?\b(?<state>.*)\b\s*?\)\s*?(?<zip>[\dA-Z]{3}\s?[\dA-Z]{3})\s*?/
    ).groups;
    const phone = storeDetails.eq(4).text().trim();
    if (phone.indexOf('pening') !== -1) {
      return
    }

    records.push({
      locator_domain: 'althotels.com',
      location_name: storeDetails.eq(0).text().trim(),
      street_address: storeDetails.eq(1).text().trim(),
      city,
      state,
      zip,
      country_code: 'CA',
      store_number: '<MISSING>',
      phone,
      location_type: '<MISSING>',
      latitude: '<MISSING>',
      longitude: '<MISSING>',
      hours_of_operation: '<MISSING>'
    })
  })

	return records;

	// End scraper

}
