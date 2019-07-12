const Apify = require('apify');

(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: 'https://www.raleys.com/store-locator/' }],
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

			// Begin scraper

			const poi = {
        locator_domain: 'https://www.raleys.com/store-locator/',
        location_name: $('title').text(),
        street_address: '1601 W Capitol Ave.,west',
        city: 'sacremento',
        state: 'CA',
        zip: '95691',
        country_code: 'US',
				store_number: '<MISSING>',
				phone: '(916) 372-3000',
				location_type: '<MISSING>',
        latitude: 37.773500,
        longitude: -122.417774,
				hours_of_operation: 'mon-fri 6am-11pm'
			};

			await Apify.pushData([poi]);

			// End scraper

    },
  });

  await crawler.run();
})();