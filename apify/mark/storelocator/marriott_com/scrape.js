const Apify = require('apify');
const {
  getLastPage,
  pushDetail,
} = require('./tools');

Apify.main(async () => {
  const initialRequest = {
    url: 'https://www.marriott.com/hotel-search.mi',
    userData: {
      urlType: 'initial',
    },
  };
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest(initialRequest);

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    launchPuppeteerOptions: {
      headless: true,
      useChrome: true,
      stealth: true,
    },
    gotoFunction: async ({
      request, page,
    }) => {
      await page.goto(request.url, {
        timeout: 0, waitUntil: 'networkidle0',
      });
    },
    maxRequestsPerCrawl: 100,
    maxConcurrency: 1,
    maxRequestRetries: 4,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        const canadaTabSelector = '.tile-directory-result > div:nth-child(5) > h3 > a';
        await page.waitForSelector(canadaTabSelector, { waitUntil: 'load', timeout: 0 });
        await page.click(canadaTabSelector);
        const enqueued = await Apify.utils.enqueueLinks({
          page,
          requestQueue,
          pseudoUrls: [
            'https://www.marriott.com/search/submitSearch.mi?destinationAddress.destination=[.*],%20USA&destinationAddress.country=US&destinationAddress.stateProvince=[.*]&searchType=InCity&filterApplied=false',
            'https://www.marriott.com/search/submitSearch.mi?destinationAddress.region=canada[.*]',
          ],
          userData: {
            urlType: 'detail',
          },
        });
        console.log(`Total urls to be pulled: ${enqueued.length}`);
        await page.waitFor(7000);
      }
      if (request.userData.urlType === 'detail') {
        const paginationSelector = '#results-pagination > div > div.l-display-inline-block > a';
        await page.waitForSelector(paginationSelector, { waitUntil: 'load', timeout: 0 });
        const paginationValues = await page.$$eval(paginationSelector, ae => ae.map(a => a.title));
        const lastPage = getLastPage(paginationValues);
        const totalPages = new Array(lastPage);

        /* eslint-disable no-restricted-syntax */
        for await (const [i, v] of totalPages.entries()) {
          const currentPage = i + 1;
          await pushDetail({ page });
          await page.waitFor(7000);
          if (currentPage < totalPages.length) {
            const nextPageSelector = '#results-pagination > div > div.l-display-inline-block > a.m-pagination-next';
            await page.waitForSelector(nextPageSelector, { waitUntil: 'load', timeout: 0 });
            await page.click(nextPageSelector);
          }
        }
      }
    },
  });

  await crawler.run();
});
