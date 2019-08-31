const Apify = require('apify');
const _ = require('underscore');
const { formatPhoneNumber } = require('./tools');

const { Poi } = require('./Poi');

const { log } = Apify.utils;

Apify.main(async () => {
  // Step 1 - Collect urls from the sitemap which shows links by states
  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto('https://www.choicehotels.com/rodeway-inn/sitemap', { waitUntil: 'networkidle0' });
  // (https:\/\/www.choicehotels.com\/(?=\S*['-])([a-zA-Z'-]+)\/rodeway-inn) - regex hotels
  const allPageUrls = await p.$$eval('a', ae => ae.map(a => a.href));
  const allStateUrls = allPageUrls.filter(l => l.match(/(https:\/\/www.choicehotels.com\/(?=\S*['-])([a-zA-Z'-]+)\/rodeway-inn)/));

  // Step 2 - Now that we've got all urls by state including Canada, pull out urls for each hotel
  let tempReq = [];
  console.log('Gathering hotel links');

  /* eslint-disable no-restricted-syntax */
  for await (const stateUrl of allStateUrls) {
    console.log(`Searching: ${stateUrl}`);
    const statePage = await browser.newPage();
    await statePage.goto(stateUrl, { waitUntil: 'networkidle0', timeout: 0 });
    await statePage.waitForSelector('.more-content', { visible: true });
    const allStatePageUrls = await statePage.$$eval('a', ae => ae.map(a => a.href));
    const hotelUrls = allStatePageUrls.filter(l => l.match(/(https:\/\/www.choicehotels.com\/(?=\S*['-])([a-zA-Z'-]+)\/(?=\S*['-])([a-zA-Z'-]+)\/rodeway-inn-hotels\/)/))
      .map(e => ({ url: e }));
    tempReq = [...tempReq, ...hotelUrls];
    await statePage.close();
  }

  await browser.close();
  console.log('Finished gathering links, initiating crawler.');
  // For test purposes -> const tempReq = data.urls;

  // Step 3 - Now that we've got all hotel urls, create a request list for the crawler
  const requestList = new Apify.RequestList({
    sources: tempReq,
  });
  await requestList.initialize();

  // Step 4 - Create the crawler
  /* eslint-disable no-unused-vars */
  const crawler = new Apify.PuppeteerCrawler({
    requestList,
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
    maxRequestsPerCrawl: 700,
    maxConcurrency: 10,
    maxRequestRetries: 1,
    handlePageTimeoutSecs: 60,
    handlePageFunction: async ({ request, page }) => {
      // Choice Hotels redirects to a new page if a hotel is not on their map (incomplete listing)
      // We're checking to make sure we aren't redirected to a generic hotel search page
      if (await page.$('#mainContent > div > div > main > div > div > div > ch-search-status-bar > div') === null) {
        await page.waitForSelector('#property > div > div > div > section > div > div.hotel-main > h1', {
          timeout: 60000, waitUntil: 'load',
        });
        console.log(request.url);
        const locationName = await page.$eval('#property > div > div > div > section > div > div.hotel-main > h1', e => e.innerText);
        const streetAddress = await page.$eval('#property > div > div > div > section > div.address > line', e => e.innerText);
        const city = await page.$eval('#property > div > div > div > section > div.address > span:nth-child(2)', e => e.innerText);
        const state = await page.$eval('#property > div > div > div > section > div.address > span:nth-child(3)', e => e.innerText);
        const zip = await page.$eval('#property > div > div > div > section > div.address > span:nth-child(4)', e => e.innerText);
        const country = await page.$eval('#property > div > div > div > section > div.address > span:nth-child(5)', e => e.innerText);
        const phone = await page.$eval('#property > div > div > div > section > div.contact > span:nth-child(2)', e => e.innerText);
        const latitude = await page.$eval('#property > div > div > div > section > div:nth-child(2) > span', e => e.getAttribute('content'));
        const longitude = await page.$eval('#property > div > div > div > section > div:nth-child(2) > span > span', e => e.getAttribute('content'));
        const poiData = {
          locator_domain: 'choicehotels.com__rodeway-inn',
          location_name: locationName,
          street_address: streetAddress,
          city,
          state,
          zip,
          country_code: country,
          phone: formatPhoneNumber(phone),
          location_type: undefined,
          latitude,
          longitude,
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },

    handleFailedRequestFunction: ({ request }) => {
      const details = _.pick(request, 'id', 'url', 'method', 'uniqueKey');
      log.error('Rodeway Inn Crawler: Request failed and reached maximum retries', { errorDetails: details });
    },
  });

	await crawler.run();
});
