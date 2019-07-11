const Apify = require('apify');

(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: 'www.alohagas.com/oahu.html' }],
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

			// Begin scraper

			const poi = {
        locator_domain: 'www.alohagas.com/oahu.html',
        location_name: $('alohagas').text(),
        street_address: '3203 Monsarrat Ave',
        city: 'Honolulu',
        state: 'HI',
        zip: '94103',
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