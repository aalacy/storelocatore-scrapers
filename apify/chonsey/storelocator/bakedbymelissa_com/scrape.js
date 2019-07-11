const Apify = require('apify');

(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: 'https://www.bakedbymelissa.com/locations' }],
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

			// Begin scraper

			const poi = {
        locator_domain: 'https://www.bakedbymelissa.com/locations',
        location_name: $('Colombus Circle').text(),
        street_address: '975 8th Ave',
        city: 'New York',
        state: 'Ny',
        zip: '10019',
        country_code: 'US',
				store_number: '<MISSING>',
				phone: '(415) 966-1152',
				location_type: '<MISSING>',
        latitude: 37.773500,
        longitude: -122.417774,
				hours_of_operation: 'mon-fri 9am-5pm'
			};

			await Apify.pushData([poi]);

			// End scraper

    },
  });

  await crawler.run();
})();