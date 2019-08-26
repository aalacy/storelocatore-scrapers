const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const records = []
  await request("https://www.btonefitness.com/locations")
    .then((html) => {
      // the location information is available in the google maps markers in the inline javascript of the page
      const regex = /(google.maps.Marker[\d\D]*?position: \{ lat: (?<lat>[-\d\.]*?), lng: (?<long>[-\d\.]*)[\d\D]*?html: \')(?<elementHTML>[\d\D]*?)(\'\s*\}\))/g;
      while ((element = regex.exec(html)) !== null) {
        var $ = cheerio.load(element.groups.elementHTML);
          var location_name = $('h3').text();
          // If the location is coming soon, we don't include it
          if (RegExp(/Coming/).test(location_name)) {
            continue
          }
          location_name = location_name.trim();

          const rawAddress = $('p').html();
          const {groups: addressParts} = rawAddress.match(/\s*(?<street_address>.+)\s*\<br\>\s*(?<city>.+),\s*(?<state>[A-Z]{2})\s*(?<zip>\d+)[\n\s]*$/);
          records.push({
            locator_domain: 'btonefitness.com',
            location_name: location_name,
            street_address: addressParts.street_address,
            city: addressParts.city,
            state: addressParts.state,
            zip: addressParts.zip,
            country_code: 'US',
            store_number: '<MISSING>',
            phone: '<MISSING>',
            location_type: '<MISSING>',
            latitude: element.groups.lat || '<MISSING>',
            longitude: element.groups.long || '<MISSING>',
            hours_of_operation: '<MISSING>',
          });
      }
    });
  return records;

	// End scraper

}
