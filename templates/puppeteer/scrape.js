const Apify = require('apify');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ url: 'https://safegraph.com/' });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
		handlePageFunction: async ({ request, page }) => {

			// Being scraper

			const heading = await page.evaluate(() => document.querySelector('h1.heading-primary').innerText);

      const poi = {
				locator_domain: 'safegraph.com',
				page_url: '<MISSING>',
        location_name: heading,
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

			// End scraper

    },
    maxRequestsPerCrawl: 100,
		maxConcurrency: 10,
		launchPuppeteerOptions: {headless: true},
  });

  await crawler.run();
});
