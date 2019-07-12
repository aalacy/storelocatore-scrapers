const Apify = require('apify');

(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: 'https://bodyalivefitness.com/kenwood/' }],
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

			// Begin scraper

			const poi = {
        locator_domain: 'https://bodyalivefitness.com/kenwood/',
        location_name: $('Kenwood').text(),
        street_address: '8100 Montgomery Rd.',
        city: 'Cincinnati',
        state: 'OH',
        zip: '45326',
        country_code: 'US',
				store_number: '<MISSING>',
				phone: '(513) 630-9352',
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