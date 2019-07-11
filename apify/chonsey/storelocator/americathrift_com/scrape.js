const Apify = require('apify');

(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: '"https://www.americasthrift.com/locations/' }],
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

			// Begin scraper

			const poi = {
        locator_domain: '"https://www.americasthrift.com/locations/',
        location_name: $('title').text(),
        street_address: '218 Second St Sw',
        city: 'Alabaster',
        state: 'AL',
        zip: '35007',
        country_code: 'US',
				store_number: '<MISSING>',
				phone: '(205) 664-0777',
				location_type: '<MISSING>',
        latitude: 37.773500,
        longitude: -122.417774,
				hours_of_operation: 'mon-sat 7:30-9pm'
			};

			await Apify.pushData([poi]);

			// End scraper

    },
  });

  await crawler.run();
})();