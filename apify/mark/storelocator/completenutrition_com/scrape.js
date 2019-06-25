const Apify = require('apify');

const {
  formatLocationString,
  formatData,
} = require('./tools');

Apify.main(async () => {
  const locationUrl = 'https://completenutrition.com/pages/retail-stores';
  const requestList = new Apify.RequestList({
    sources: [{ url: locationUrl }],
  });
  await requestList.initialize();

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    handlePageFunction: async ({ page }) => {
      const allParagraphElements = await page.$$eval('p', se => se.map(s => s.innerText));
      const locationStrings = allParagraphElements.filter(e => e.includes('Complete Nutrition') && !e.includes('2019'));
      /* eslint-disable no-restricted-syntax */
      for await (const locationString of locationStrings) {
        const formattedString = formatLocationString(locationString);
        const poi = {
          locator_domain: 'completenutrition.com',
          ...formattedString,
        };
        await Apify.pushData(formatData(poi));
      }
    },
    maxRequestsPerCrawl: 1,
    maxConcurrency: 1,
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
        timeout: 0, waitUntil: 'load',
      }),
  });

  await crawler.run();
});
