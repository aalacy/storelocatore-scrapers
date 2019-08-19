const Apify = require('apify');
const request = require('request-promise');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const records = [];
  const { data } = JSON.parse(await request.get({
    url: 'https://www.aquaaston.com/sites/aah/home/hotels.parametricSearch.do?destinationId=&startDate=2019-08-15&endDate=2050-08-31',
    headers: {
      'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15',
      Accept: 'application/json, text/javascript, */*; q=0.01'
    }
  }));

  for (const poiData of data) {
    records.push({
      locator_domain: 'aquaaston.com',
      location_name: poiData.name,
      street_address: '<MISSING>',
      city: poiData.location_name || '<MISSING>',
      state: '<MISSING>',
      zip: '<MISSING>',
      country_code: '<MISSING>',
      store_number: poiData.id,
      phone: poiData.phoneNumber,
      location_type: poiData.typeDesc.join(' '),
      latitude: poiData.location.latitude,
      longitude: poiData.location.longitude,
      hours_of_operation: '<MISSING>'
    })
  }

	return records;

	// End scraper

}
