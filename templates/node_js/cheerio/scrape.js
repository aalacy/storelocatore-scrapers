const Apify = require('apify');

(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: 'http://safegraph.com' }],
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

			// Begin scraper

			const poi = {
				locator_domain: 'safegraph.com',
				page_url: '<MISSING>',
        location_name: $('title').text(),
        street_address: '1543 mission st',
        city: 'san francisco',
        state: 'CA',
        zip: '94107',
        country_code: 'US',
				store_number: '<MISSING>',
				phone: '<MISSING>',
				location_type: '<MISSING>',
        latitude: 37.773500,
        longitude: -122.417774,
				hours_of_operation: '<MISSING>'
			};

			await Apify.pushData([poi]);

			// End scraper

    },
  });

  await crawler.run();
})();
