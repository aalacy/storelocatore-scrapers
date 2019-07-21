const Apify = require('apify')
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const rootAddress = 'https://www.brothers-marketplace.com';
  const records = [];
  await request({
    url: rootAddress,
    headers: {
      'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15"
    }
  })
    .then(async function (html) {
      const $ = cheerio.load(html);

      // individual stores are in .col elements
      $(".col").each((_, storeElement) => {
        const location_name = $("h2", storeElement).text();
        const rawAddress = $('p', storeElement).text();
        const {groups: addressParts} = rawAddress.match(/\s*(?<street_address>.+)\n(?<hours>.+\n.+)\n(?<phone>[.\d]*)/)
        records.push({
          locator_domain: 'brothers-marketplace_com',
          location_name: location_name,
          street_address: addressParts.street_address,
          // location_name appears to be city name
          city: location_name,
          // state is not given with each location, but it is the same across all
          state: 'MA',
          zip: '<MISSING>',
          country_code: 'US',
          store_number: '<MISSING>',
          phone: addressParts.phone,
          location_type: '<MISSING>',
          latitude: '<MISSING>',
          longitude: '<MISSING>',
          hours_of_operation: addressParts.hours,
        });
      });
    });

  return records;
	// End scraper

}
