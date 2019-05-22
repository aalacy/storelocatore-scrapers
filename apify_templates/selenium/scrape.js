const Apify = require('apify');
const { Capabilities, Builder, By, until, logging } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');

Apify.main(async () => {
	const webDriver = await Apify.launchWebDriver();

	await webDriver.get("https://safegraph.com");

	const pois = await webDriver.executeScript(() => {
		// Replace this with your actual scraper
		const poi = {
			locator_domain: "safegraph.com",
			location_name: "safegraph",
			street_address: "1543 mission st",
			city: "san francisco",
			state: "CA",
			zip: "94107",
			country_code: "US",
			store_number: null,
			phone: null,
			location_type: null,
			naics_code: "518210",
			latitude: -122.417774,
			longitude: -122.417774,
			hours_of_operation: null,
		};
		return [poi];
	});

	await Apify.pushData(pois);
});
