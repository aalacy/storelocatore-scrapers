const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const rootAddress = 'https://buckhorngrill.com/location/';
  const records = [];

  await request.get(rootAddress)
  .then(html => {
    const $ = cheerio.load(html);

    // locations are in .location-row div elements in a .location-archive div
    $('.location-archive .location-row .loc-col:first-of-type').each((_, locationElement) => {
      const location_name = $('h4', locationElement).text();
      const rawAddress = $('p:first-of-type', locationElement).text();
      // inconsistencies in the source page formatting make it difficult to parse the street address
      // from the city, state, zip code. Some are separated by commas, some by space, some have 
      // multi-word cities, etc.
      // const {groups: addressParts} = rawAddress.match(/\s*(?<street_address>.*)/)
      // const {groups: addressParts} = rawAddress.match(/^[\d\D]*(?<state>[A-Z]{2})\s*(?<zip>[\d-]*)[\n\s]*$/);
      // 5614 Bay Street Suite#238 Emeryville, CA 94608
      const phone = $('p:nth-of-type(2)', locationElement).text().match(/[\d\D]*\[P\]\s([\d\D]+?)\s[\d\D]*/)[1];
      const location_hours = $('p:nth-of-type(3)', locationElement).text();
      records.push({
        locator_domain: 'buckhorngrill.com',
        location_name: location_name,
        raw_address: rawAddress,
        street_address: '<INACCESSIBLE>',
        city: '<INACCESSIBLE>',
        state: '<INACCESSIBLE>',
        zip: '<INACCESSIBLE>',
        country_code: 'US',
        store_number: '<MISSING>',
        phone: phone,
        location_type: '<MISSING>',
        latitude: '<MISSING>',
        longitude: '<MISSING>',
        hours_of_operation: location_hours,
      });
    })
  })
  .catch(error => {
    throw `Request failed with error:${error}`;
  })
  return records;

	// End scraper

}
