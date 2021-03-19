const Apify = require('apify');
const requestPromise = require('request-promise');

(async() => {
	const requestList = new Apify.RequestList({
		sources: [{ url: 'http://safegraph.com' }],
	});
	await requestList.initialize();

	const crawler = new Apify.BasicCrawler({
		requestList,
		handleRequestFunction: async ({ request }) => {

			// Begin scraper

			const html = await requestPromise(request.url);
			const urlStart = html.indexOf("data-wf-domain=") + 16
			const fromUrlStart = html.substring(urlStart);
			const safegraphUrl = fromUrlStart.substring(0, fromUrlStart.indexOf("\"")); 

			const poi = {
				locator_domain: safegraphUrl,
				page_url: '<MISSING>',
				location_name: 'safegraph',
				street_address: '1543 mission st',
				city: 'san francisco',
				state: 'CA',
				zip: '94107',
				country_code: 'US',
				store_number: "<MISSING>",
				phone: "<MISSING>",
				location_type: "<MISSING>",
				latitude: 37.773500,
				longitude: -122.417774,
				hours_of_operation: "<MISSING>",
			};
			await Apify.pushData([poi]);

			// End scraper

		},
	});

	await crawler.run();
})();
