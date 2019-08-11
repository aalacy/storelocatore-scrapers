const Apify = require('apify');
const request = require('request-promise');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  responses = [];

  const json = await request.post({
    url: 'https://www.conniespizza.com/wp-admin/admin-ajax.php',
    form:{
      'lat':'41.8490794',
      'lng':'-87.6408113',
      'radius':'50000',
      'action':'csl_ajax_onload'
    }
  })

  for (const response of JSON.parse(json).response) {
    const {
      name: location_name,
      address: street_address,
      address2,
      city,
      state,
      zip,
      lat: latitude,
      lng: longitude,
      id: store_number,
    } = response;
    responses.push({
      locator_domain: 'conniespizza.com',
      location_name,
      street_address,
      city,
      state,
      zip,
      country_code: 'US',
      store_number,
      phone: '<MISSING>',
      location_type: '<MISSING>',
      latitude,
      longitude,
      hours_of_operation: '<MISSING>',
    });
  }

	return responses;

	// End scraper

}
