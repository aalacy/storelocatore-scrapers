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
  const rootAddress = new URL('https://www.cafegratitude.com/#locations');
  const $ = cheerio.load(await request.get(rootAddress.href));

  for (const locationElem of $('#locations .col-sm-6 .caption').get()) {
    const {street_address, city, state, zip} = $('p:nth-child(3)', locationElem).text().trim().match(
      /^(?<street_address>.{3,}),\s(?<city>.{2,}),\s(?<state>[A-Z]{2})\s(?<zip>[\d\s]{5,10})$/
      ).groups
    records.push({
      locator_domain: 'cafegratitude.com',
      location_name: $('h3', locationElem).text().trim(),
      street_address,
      city,
      state,
      zip,
      country_code: 'US',
      store_number: '<MISSING>',
      phone: $('p:nth-child(4)', locationElem).text().trim(),
      location_type: '<MISSING>',
      latitude: '<MISSING>',
      longitude: '<MISSING>',
      hours_of_operation: $('p:nth-child(5)', locationElem).text().trim()
    });
  }

	return records;

	// End scraper

}
