const Apify = require('apify');
const {
  formatGeoLocation,
  formatCityState,
  formatStreetAddress,
  formatPhoneNumber,
  formatHours,
} = require('./tools');

const { Poi } = require('./Poi');

Apify.main(async () => {
  const browser = await Apify.launchPuppeteer({ headless: true });
  const p = await browser.newPage();
  await p.goto('https://www.shopversona.com/versonastores.cfm', { waitUntil: 'networkidle0' });
  const stateSelector = await p.$$eval('option', oe => oe.map(o => o.value));
  const pathTemplate = 'https://www.shopversona.com/versonastores.cfm?locRad=10&locZip=&locSt=';
  const reqUrls = stateSelector.filter(e => e.match(/^[A-Z]{2}$/)).map(e => ({ url: `${pathTemplate}${e}` }));
  await browser.close();

  const requestList = new Apify.RequestList({
    sources: reqUrls,
  });
  await requestList.initialize();

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
    maxRequestsPerCrawl: 100,
    maxConcurrency: 10,
    handlePageFunction: async ({ request, page }) => {
      await page.waitForSelector('.mapAddress');

      // Get the address info
      const storeInfoBlock = await page.$$eval('.mapAddress', me => me.map(m => m.innerText));
      const blockArrays = storeInfoBlock.map(e => e.split('\n'));

      // Get geolocation info
      const onclickValue = await page.$$eval('.mapAddress > h4', he => he.map(h => h.getAttribute('onclick')));
      const geoLocation = onclickValue.map(g => g.substring((g.indexOf(',') + 1), g.indexOf(')')));

      // Get zip codes
      const allUrls = await page.$$eval('a', ae => ae.map(a => a.href));
      const zipCodes = allUrls.filter(e => e.match(/[0-9]{5}/))
        .map(u => u.substring((u.indexOf('&sll') - 5), u.indexOf('&sll')));

      /* eslint-disable no-restricted-syntax */
      for await (const [index, storeDetails] of blockArrays.entries()) {
        const cityStateObj = formatCityState(storeDetails[0]);
        const latLong = formatGeoLocation(geoLocation[index]);

        const poiData = {
          locator_domain: 'shopversona__com',
          location_name: storeDetails[1],
          street_address: formatStreetAddress(storeDetails[2]),
          ...cityStateObj,
          zip: zipCodes[index],
          store_number: undefined,
          phone: formatPhoneNumber(storeDetails[3]),
          naics_code: undefined,
          ...latLong,
          ...((storeDetails.length < 8) && { hours_of_operation: undefined }),
          ...((storeDetails.length > 8) && {
            hours_of_operation: formatHours(storeDetails[5], storeDetails[6]),
          }),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();
});

