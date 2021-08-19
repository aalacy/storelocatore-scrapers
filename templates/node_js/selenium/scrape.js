const Apify = require('apify');
const { Capabilities, Builder, By, until, logging } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');

Apify.main(async () => {
  const webDriver = await Apify.launchWebDriver({headless: true, 'args': ['--headless', '--no-sandbox', '--disable-dev-shm-usage']});

  await webDriver.get('https://safegraph.com');

  const pois = await webDriver.executeScript(() => {

		// Begin scraper

		const poi = {
			locator_domain: 'safegraph.com',
			page_url: '<MISSING>',
      location_name: 'safegraph',
      street_address: '1543 mission st',
      city: 'san francisco',
      state: 'CA',
      zip: '94107',
      country_code: 'US',
			store_number: '<MISSING>',
			phone: '<MISSING>',
			location_type: '<MISSING>',
      naics_code: '518210',
      latitude: -122.417774,
      longitude: -122.417774,
			hours_of_operation: '<MISSING>',
    };
		return [poi];
		
		// End scraper
	
	});

	await Apify.pushData(pois);

});
