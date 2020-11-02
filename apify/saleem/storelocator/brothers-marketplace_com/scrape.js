const Apify = require('apify')
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const rootAddress = 'http://rochemarket.wpengine.com/locations/';
  const records = [];
  await request({
    url: rootAddress,
    headers: {
      'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15"
    }
  })
    .then(async function (html) {
      const $ = cheerio.load(html);
      
      const pois = [...$('.entry-content').text().trim().matchAll(/(?<location_name>[A-Z]{3,})[\d\D]*?\n(?<street_address>\d+ .*)\b\s*?\n(?<hours>[\d\D]*?)\b(?<phone>\d{3}\.\d{3}.\d{4})\b/g)];
      
      for (const poi of pois) {
        const { location_name, street_address, hours, phone} = poi.groups;
        records.push({
          locator_domain: 'rochemarket.wpengine.com',
          location_name: location_name,
          street_address: street_address,
          // location_name appears to be city name
          city: location_name,
          // state is not given with each location, but it is the same across all
          state: 'MA',
          zip: '<MISSING>',
          country_code: 'US',
          store_number: '<MISSING>',
          phone: phone,
          location_type: '<MISSING>',
          latitude: '<MISSING>',
          longitude: '<MISSING>',
          hours_of_operation: hours,
        });
      }
    });

  return records;
	// End scraper

}
