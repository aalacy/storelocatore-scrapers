const Apify = require('apify');
const requestPromise = require('request-promise');

(async() => {
	const requestList = new Apify.RequestList({
		sources: [{ url: 'https://www.birkenstock.com/us/storelocator' }],
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
				locator_domain: 'https://www.birkenstock.com/us/storelocator',
				location_name:  'BirkenstockStore',
				street_address: '120 Spring  st',
				city: 'New York',
				state: 'NY',
				zip: '10012',
				country_code: 'US',
				store_number: "<MISSING>",
				phone: "(646) 890-6940",
				location_type: "<MISSING>",
				latitude: 37.773500,
				longitude: -122.417774,
				hours_of_operation: "mon-fri 10am-8pm",
			};
			await Apify.pushData([poi]);

			// End scraper

		},
	});

	await crawler.run();
})();