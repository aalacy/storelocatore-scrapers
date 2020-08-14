const Apify = require('apify');
const randomUA = require('modern-random-ua');
const { lookupByState, states } = require('zipcodes');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

function formatPhone(phone) {
  return phone ? phone.replace(/\-/g, '') : null;
}

function formatHoursOfOperation(start, end) {
  if (!start && !end) {
    return null;
  }

  return end ? `${start}-${end}` : start;
}

function getLocationUrls() {
  const stateAbbrs = Object.keys(states.abbr);
  return stateAbbrs
    .map((state) => {
      try {
        const loc = lookupByState(state);
        if (!loc || !loc[0]) return;

        const { latitude, longitude, country } = loc[0];
        const url = `https://www.wawa.com/Handlers/LocationByLatLong.ashx?limit=500&lat=${latitude}&long=${longitude}`;
        return {
          url,
          userData: {
            country_code: country,
          },
        };
      } catch (err) {
        console.log(err);
      }
    })
    .filter((url) => url);
}

Apify.main(async () => {
  const locationUrls = getLocationUrls();
  const locationMap = {};
  const requestList = await Apify.openRequestList('location-data', locationUrls);

  const useProxy = process.env.USE_PROXY;
  const proxyConfiguration = await Apify.createProxyConfiguration({
    groups: ['RESIDENTIAL'], // List of Apify Proxy groups
    countryCode: 'US',
  });

  const puppeteerPoolOptions = {
    retireInstanceAfterRequestCount: 1,
  };

  const launchPuppeteerOptions = {
    headless: true,
    stealth: true,
    useChrome: true,
    useApifyProxy: !!useProxy,
    userAgent: randomUA.generate(),
    ignoreHTTPSErrors: true,
  };

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    launchPuppeteerOptions,
    puppeteerPoolOptions,
    proxyConfiguration,
    maxConcurrency: 10,
    maxRequestsPerCrawl: 50,
    async handlePageFunction({ request, page }) {
      const serializedJSON = await page.evaluate(() => {
        const selected = document.body.querySelector('pre');
        return selected ? selected.textContent : null;
      });

      if (!serializedJSON) return;

      try {
        data = JSON.parse(serializedJSON);

        const pois = data.locations.map((location) => {
          // validate that there is no duplicate
          if (locationMap[location.locationID]) {
            return;
          }

          const { storeNumber, storeName, telephone, storeOpen, storeClose, addresses } = location;
          const [friendly, physical] = addresses;

          const poi = {
            locator_domain: 'wawa.com',
            page_url: request.url,
            location_name: getOrDefault(storeName),
            store_number: getOrDefault(storeNumber),
            street_address: getOrDefault(friendly.address),
            city: getOrDefault(friendly.city),
            state: getOrDefault(friendly.state),
            zip: getOrDefault(friendly.zip),
            country_code: request.userData.country_code,
            latitude: physical.loc[0],
            longitude: physical.loc[1],
            phone: getOrDefault(formatPhone(telephone)),
            hours_of_operation: getOrDefault(formatHoursOfOperation(storeOpen, storeClose)),
            location_type: MISSING,
          };

          locationMap[location.locationID] = 1;
          return poi;
        });
        const nullRemoved = pois.filter((poi) => poi);
        await Apify.pushData(nullRemoved);
      } catch (err) {
        console.log(err);
      }
    },
  });

  await crawler.run();
});
