const Apify = require('apify');
const BASE_URL = 'https://www.wawa.com';
const SITEMAP = 'site-map';

async function handlePageFunction({ request, page }) {
  // Begin scraper
  const siteMapLinks = await page.$('a.CMSSiteMapLink');
  await setTimeout(() => {}, 2000);
  console.log(siteMapLinks);
  siteMapLinks.each(async (link) => {
    const href = await link.attr('href');
    console.log(href);
  });
}

Apify.main(async () => {
  const url = `${BASE_URL}/${SITEMAP}`;
  const requestQueue = await Apify.openRequestQueue();
  requestQueue.addRequest({ url });
  const useProxy = process.env.USE_PROXY;

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction,
    maxConcurrency: 1,
    maxRequestsPerCrawl: 1,
    launchPuppeteerOptions: {
      headless: false,
      stealth: true,
      useChrome: true,
      useApifyProxy: !!useProxy,
    },
  });

  await crawler.run();
});
