const Apify = require('apify');

(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: '"https://www.billskhakis.com/store-locator/' }],
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

			// Begin scraper

			const poi = {
        locator_domain: '"https://www.billskhakis.com/store-locator/',
        location_name: $('Binghams').text(),
        street_address: '827 E Broadway',
        city: 'Colombia',
        state: 'MO',
        zip: '65201',
        country_code: 'US',
				store_number: '<MISSING>',
				phone: '673-442-6397',
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