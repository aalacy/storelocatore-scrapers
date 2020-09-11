const Apify = require('apify');
const zipcodes = require('zipcodes');
const { log } = Apify.utils;

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

function getLocationUrls(stateAbbrs) {
  const { lookupByState } = zipcodes;
  const urls = stateAbbrs
    .map((state) => {
      try {
        const zips = lookupByState(state);
        if (!zips || !zips.length) return;
        const randomZipCodes = pickRandom(zips, Math.ceil(zips.length / 3));

        return randomZipCodes.map((zipcode) => {
          const { latitude, longitude, country } = zipcode;
          const url = `https://www.wawa.com/Handlers/LocationByLatLong.ashx?limit=500&lat=${latitude}&long=${longitude}`;

          return {
            url,
            userData: {
              country_code: country,
            },
          };
        });
      } catch (err) {
        log.error(err);
      }
    })
    .filter((url) => url);

  return urls.reduce((total, locations) => {
    total.push(...locations);
    return total;
  }, []);
}

function pickRandom(array, sampleSize) {
  const population = [...array];
  const sample = [];
  for (let i = 0; i < sampleSize; i++) {
    const index = Math.floor(Math.random() * population.length);
    const [item] = population.splice(index, 1);
    sample.push(item);
  }
  return sample;
}

async function scrapeStates({ requestQueue, $ }) {
  const states = $('#drpState option')
    .map(function () {
      return $(this).attr('value');
    })
    .toArray()
    .filter((el) => el !== 'All');

  const locationsUrls = getLocationUrls(states);
  log.info(`zipcode count: ${locationsUrls.length} \n`);
  const promises = locationsUrls.map((url) => requestQueue.addRequest(url));
  return Promise.all(promises);
}

async function scrapeLocations({ request, body, locationMap }) {
  if (!body) return;

  const serializedData = body.toLocaleString();
  try {
    data = JSON.parse(serializedData);

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

      locationMap[location.locationID] = true;
      return poi;
    });

    const nullRemoved = pois.filter((poi) => poi);
    await Apify.pushData(nullRemoved);
  } catch (error) {
    request.pushErrorMessage(JSON.stringify({ error, data: serializedData }));
  }
}

Apify.main(async () => {
  const locationMap = {};
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.wawa.com/fresh-food/wawa-delivery',
    userData: {
      pageType: 'states',
    },
  });

  const proxyPassword = process.env.PROXY_PASSWORD;
  const proxyConfiguration = await Apify.createProxyConfiguration({
    groups: ['RESIDENTIAL'], // List of Apify Proxy groups
    countryCode: 'US',
    password: proxyPassword,
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    useSessionPool: true,
    persistCookiesPerSession: true,
    additionalMimeTypes: ['text/json'],
    // launchPuppeteerOptions,
    // puppeteerPoolOptions,
    proxyConfiguration,
    maxConcurrency: 1000,
    maxRequestsPerCrawl: 10000,
    async handlePageFunction({ request, $, body }) {
      switch (request.userData.pageType) {
        case 'states':
          await scrapeStates({ $, requestQueue });
          break;
        default:
          await scrapeLocations({ body, request, locationMap });
      }
    },
  });

  await crawler.run();
  log.info('\n------------------------------');
  log.info(`final location count: ${Object.keys(locationMap).length}`);
});
