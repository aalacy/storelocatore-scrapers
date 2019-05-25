const Apify = require('apify');

Apify.main(async () => {
	const data = await scrape();
	await Apify.pushData(data);
});

async function scrape() {
	// Replace this with your actual scraper
	const record = {
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
	return [record];
}
