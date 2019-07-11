const Apify = require('apify');

(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: '"https://www.bankunited.com/branch-locator' }],
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

			// Begin scraper

			const poi = {
        locator_domain: '"https://www.bankunited.com/branch-locator',
        location_name: $('title').text(),
        street_address: '252 Broadway ',
        city: 'Brooklyn',
        state: 'NY',
        zip: '11211',
        country_code: 'US',
				store_number: '<MISSING>',
				phone: '1-877-779-2265',
				location_type: '<MISSING>',
        latitude: 37.773500,
        longitude: -122.417774,
				hours_of_operation: '9am-2pm'
			};

			await Apify.pushData([poi]);

			// End scraper

    },
  });

  await crawler.run();
})();