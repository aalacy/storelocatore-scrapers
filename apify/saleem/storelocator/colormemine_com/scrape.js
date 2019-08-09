const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const rootAddresses = [
    'https://www.colormemine.com/wp-admin/admin-ajax.php?action=store_search&lat=47.67012&lng=-122.11824&max_results=100&search_radius=5000',
    'https://www.colormemine.com/wp-admin/admin-ajax.php?action=store_search&lat=41.34693&lng=-72.90471&max_results=100&search_radius=5000',
    'https://www.colormemine.com/wp-admin/admin-ajax.php?action=store_search&lat=41.1319&lng=-96.05733&max_results=100&search_radius=5000'
  ]
  const idIsLoaded = {};
  const records = [];

  const promises = rootAddresses.map(async address => {
    return request.get(address).then(json => {
      for (const location of JSON.parse(json)) {
        if (idIsLoaded[location.id] || location.store.indexOf('Coming Soon') !== -1) {
          continue
        }
        idIsLoaded[location.id] = true;
        let {
          store: location_name,
          id: store_number,
          city,
          state,
          zip,
          country: country_code,
          lat: latitude,
          lng: longitude,
          phone
        } = location;
        if (zip === "") {
          zip = "<MISSING>";
        }
        records.push({
          locator_domain: 'colormemine.com',
          location_name,
          street_address: `${location.address} ${location.address2}`,
          city,
          state,
          zip,
          country_code,
          store_number,
          phone,
          location_type: '<MISSING>',
          latitude,
          longitude,
          hours_of_operation: cheerio.load(location.hours).text(),
        });
      }
    });
  });

  await Promise.all(promises);


	return records;

	// End scraper

}
