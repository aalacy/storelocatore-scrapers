const Apify = require('apify');

const {
  qualityMartScrape,
  qualityPlusScrape,
  goGasScrape,
  hospitalityScrape,
  serviceScrape,
  tankLineScrape,
} = require('./pageSections');

Apify.main(async () => {
  const locationUrl = 'https://www.qualityoilnc.com/locations';
  const requestList = new Apify.RequestList({
    sources: [{ url: locationUrl }],
  });
  await requestList.initialize();

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ page }) => {
      await qualityMartScrape(page);
      await qualityPlusScrape(page);
      await goGasScrape(page);
      await hospitalityScrape(page);
      await serviceScrape(page);
      await tankLineScrape(page);
    },
    maxRequestsPerCrawl: 1,
    maxConcurrency: 1,
    launchPuppeteerOptions: {
      headless: true,
    },
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
        timeout: 0, waitUntil: 'load',
      }),
  });

  await crawler.run();
});
