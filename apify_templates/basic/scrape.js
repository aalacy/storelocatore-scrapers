const Apify = require('apify');

Apify.main(async () => {
	const requestList = new Apify.RequestList({
		sources: [
			{ url: 'http://safegraph.com' },
		],
	});
	await requestList.initialize();

	const crawler = new Apify.BasicCrawler({
		requestList,
		handleRequestFunction: async ({ request }) => {
			// Replace this with your actual scrape
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
			await Apify.pushData([poi]);
		}
	});

	await crawler.run();
});
