const Apify = require('apify');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ url: 'https://safegraph.com/' });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ request, page }) => {
      // Replace this with your actual scrape
      const poi = {
        locator_domain: 'safegraph.com',
        location_name: 'safegraph',
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
				hours_of_operation: '<MISSING>',
      };
      await Apify.pushData([poi]);
    },
    maxRequestsPerCrawl: 100,
		maxConcurrency: 10,
		launchPuppeteerOptions: {headless: true},
  });

  await crawler.run();
});
