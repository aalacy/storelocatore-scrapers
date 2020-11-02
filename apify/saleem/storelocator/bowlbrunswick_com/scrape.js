const Apify = require('apify');
const request = require('request-promise');


Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {
  // Begin scraper
  const rootAddress = 'https://www.bowlbrunswick.com/bowlero-location/finder?_format=json';
  const records = [];
  await request.get(rootAddress)
    .then((json) => {
      return JSON.parse(json).forEach(location => {
        // Non-existent hours is an indication of temporarily or permanently closed
        if (!location.hours[0]) { return };
        // Check US vs. Canada. Canada has the province in the city and state is blank
        if (location.state === "") {
          [location.state] = location.city.match(/(?<=\,\s).{2,3}$/);
          [location.city] = location.city.match(/.*(?=\,)/);
          location.country_code = 'CA';
        }
        records.push({
          locator_domain: 'bowlbrunswick.com',
          location_name: location.name,
          street_address: location.address1,
          city: location.city,
          state: location.state,
          zip: location.zip,
          country_code: location.country_code || 'US',
          store_number: location.centerNumber,
          phone: location.phone || "<MISSING>",
          location_type: location.brand,
          latitude: location.lat,
          longitude: location.lng,
          hours_of_operation: JSON.stringify(location.hours)
        });      
      });
    })
  return records;
    // End scraper

}