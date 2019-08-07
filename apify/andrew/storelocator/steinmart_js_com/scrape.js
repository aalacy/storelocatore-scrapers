const Apify = require('apify');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.steinmart.com/store-locator/all-stores.do'
  });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
		// Being scraper
    handlePageFunction: async ({ request, page }) => {
  		const urls = await page.evaluate(
        () => Array.from(
          document.querySelectorAll('div.ml-storelocator-item-wrapper a'),
          a => 'https://www.steinmart.com' + a.getAttribute('href')
        )
      );
      for (const url of urls) {
        const res = await requestQueue.addRequest({
          url: url
        })
      }
      await crawlerStores.run()
    },
		launchPuppeteerOptions: {headless: true},
  });

  const crawlerStores = new Apify.PuppeteerCrawler({
    requestQueue,
    // Being scraper
    handlePageFunction: async ({ request, page }) => {
      console.log('hi')
    },
    maxConcurrency: 100,
    launchPuppeteerOptions: {headless: true},
  });
  await crawler.run();
});
