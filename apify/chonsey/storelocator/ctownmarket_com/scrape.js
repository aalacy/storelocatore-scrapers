const Apify = require('apify');

(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: 'https://locations.ctownsupermarkets.com/' }],
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

			// Begin scraper

			const poi = {
        locator_domain: 'https://locations.ctownsupermarkets.com/',
        location_name: $('Ctown').text(),
        street_address: '885 Bergen Ave',
        city: 'Jersey City',
        state: 'NJ',
        zip: '94103',
        country_code: 'US',
				store_number: '<MISSING>',
				phone: '(201) 795-1740',
				location_type: '<MISSING>',
        latitude: 37.773500,
        longitude: -122.417774,
				hours_of_operation: 'mon-fri 7am-8:30pm'
			};

			await Apify.pushData([poi]);

			// End scraper

    },
  });

  await crawler.run();
})();