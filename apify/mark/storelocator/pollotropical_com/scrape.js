const Apify = require('apify');
const {
  submitButton,
  viewAllLocationSelector,
  locationNameSelector,
  addressSelector,
  phoneSelector,
  detailLocationNameSelector,
  detailhourSelector,
  detailLatitudeSelector,
  detailLongitudeSelector,
} = require('./selectors');

const {
  getDataKey,
  getStoreNumber,
  formatPhoneNumber,
  formatAddress,
  formatHours,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const dataStorage = await Apify.openKeyValueStore('tempData');
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.pollotropical.com/locations',
    userData: {
      urlType: 'initial',
    },
  });

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
        timeout: 30000, waitUntil: 'networkidle0',
      });
    },
    maxRequestsPerCrawl: 3000,
    maxConcurrency: 10,
    handlePageFunction: async ({ request, page }) => {
      if (request.userData.urlType === 'initial') {
        // Check if the page shows the view all location element
        if (await page.$(viewAllLocationSelector) === null) {
          await page.$eval('input[name=address]', el => el.value = 'United States');
          await page.click(submitButton);
          await page.waitFor(10000);
        }
        await page.click(viewAllLocationSelector);
        await page.waitFor(10000);
        const locationNameRaw = await page.$$eval(locationNameSelector, le => le
          .map(l => l.innerText));
        const addressRaw = await page.$$eval(addressSelector, ae => ae.map(a => a.innerText));
        const phoneNumberRaw = await page.$$eval(phoneSelector, pe => pe.map(p => p.innerText));

        // Temporarily Set Info to add to later
        /* eslint-disable no-restricted-syntax */
        for await (const [i, name] of locationNameRaw.entries()) {
          const address = formatAddress(addressRaw[i]);
          const phoneStringRaw = phoneNumberRaw[i];
          const phoneArrayRaw = phoneStringRaw.replace(/\n/g, ',').split(',');
          const phoneArrayNumber = phoneArrayRaw.filter(e => e.match(/[0-9]{3}-[0-9]{4}/));
          const phoneNumber = phoneArrayNumber[0];
          const key = getDataKey(name);
          const poiData = {
            locator_domain: 'pollotropical.com',
            location_name: name,
            store_number: getStoreNumber(name),
            ...address,
            phone: phoneNumber,
          };
          await dataStorage.setValue(key, poiData);
        }
        // Look deeper to find geolocation
        await page.waitFor(5000);
        await Apify.utils.enqueueLinks({
          page,
          requestQueue,
          selectors: 'div.styles__StyledCardLinks-s1y7dfjk-2.jAGAES > a',
          pseudoUrls: [
            'https://olo.pollotropical.com/menu/[.*]',
          ],
          userData: {
            urlType: 'detail',
          },
        });
      }
      if (request.userData.urlType === 'detail') {
        // Some pages have empty information for stores -> if they do skip them
        if (await page.$(detailLocationNameSelector) !== null) {
          const detailLocationName = await page.$eval(detailLocationNameSelector, n => n.innerText);
          const latitude = await page.$eval(detailLatitudeSelector, la => la.getAttribute('title'));
          const longitude = await page.$eval(detailLongitudeSelector, lo => lo.getAttribute('title'));
          const detailHourRaw = await page.$eval(detailhourSelector, h => h.innerText);
          const key = getDataKey(detailLocationName);
          /* eslint-disable camelcase */
          const hours_of_operation = formatHours(detailHourRaw);
          const currentStoreData = await dataStorage.getValue(key);
          if (currentStoreData) {
            const revisedStoreData = {
              ...currentStoreData,
              latitude,
              longitude,
              hours_of_operation,
            };
            // Upload new
            await dataStorage.setValue(key, revisedStoreData);
          }
        }
      }
    },
  });

  await crawler.run();
  if (requestQueue.isFinished()) {
    await dataStorage.forEachKey(async (key) => {
      if (key) {
        const locationInfo = await dataStorage.getValue(key);
        const poi = new Poi(locationInfo);
        await Apify.pushData(poi);
      }
    });
  }
});
