const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  // All locations are well with 500 miles of the corporate address.
  const rootAddress = "http://www.budschicken.com/wp-admin/admin-ajax.php?action=store_search&lat=26.5386936&lng=-80.0814292&max_results=100&radius=500";
  const records = [];

  await request.get(rootAddress,{
    // requires a user-agent for the server to accept the request
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    }
  })
  .then(json => {
    JSON.parse(json).forEach(location => {
      records.push({
        locator_domain: 'budschicken.com',
        location_name: location.store,
        street_address: `${location.address} ${location.address2}`,
        city: location.city,
        state: location.state,
        zip: location.zip,
        country_code: 'US',
        store_number: location.id,
        phone: location.phone,
        location_type: '<MISSING>',
        latitude: location.lat,
        longitude: location.lng,
        hours_of_operation: cheerio.load('<table class=\"wpsl-opening-hours\"><tr><td>Monday</td><td><time>10:30 AM - 9:30 PM</time></td></tr><tr><td>Tuesday</td><td><time>10:30 AM - 9:30 PM</time></td></tr><tr><td>Wednesday</td><td><time>10:30 AM - 9:30 PM</time></td></tr><tr><td>Thursday</td><td><time>10:30 AM - 9:30 PM</time></td></tr><tr><td>Friday</td><td><time>10:30 AM - 9:30 PM</time></td></tr><tr><td>Saturday</td><td><time>10:30 AM - 9:30 PM</time></td></tr><tr><td>Sunday</td><td><time>10:30 AM - 9:30 PM</time></td></tr></table>').text(),
      });
    });
  })
  .catch(error => {
    throw `Request failed with error: ${error}`
  })

	return records;

	// End scraper

}
