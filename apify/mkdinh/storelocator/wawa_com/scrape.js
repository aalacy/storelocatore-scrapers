const Apify = require('apify');

const MISSING = '<MISSING>';

const DEFAULT_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
  Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Language': 'en-US,en;q=0.5',
  'Accept-Encoding': 'gzip, deflate, br',
  DNT: 1,
  Connection: 'keep-alive',
  'Upgrade-Insecure-Requests': 1,
  Pragma: 'no-cache',
  'Cache-Control': 'no-cache',
};

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

async function getSiteMapLinks(page) {
  return await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.CMSSiteMapLink')).map((el) =>
      el.getAttribute('href')
    );
  });
}

function generateLocationUrls(links) {
  const locationIds = links
    .map((link) => {
      const matched = link.match(/\/stores\/(\d+)\/.*/);
      return matched ? matched[1] : null;
    })
    .filter((id) => id);

  return locationIds.map(
    (id) => `https://www.wawa.com/Handlers/LocationByStoreNumber.ashx?storeNumber=${parseInt(id)}`
  );
}

async function fetchLocations(
  page,
  locationUrls,
  locations = [],
  maxAttempts = 10,
  currentAttempts = 0
) {
  console.log('-'.repeat(50));
  console.log(`attempt #${currentAttempts} to fetch: ${locationUrls.length} locations`);
  console.log('-'.repeat(50));

  const results = await page.evaluate((urls) => {
    return new Promise((resolve) => {
      const promises = urls.map(
        (url) =>
          new Promise((resolve, reject) => {
            fetch(url)
              .then((response) => response.json())
              .then((data) => resolve({ url, data }))
              .catch(() => reject(url));
          })
      );
      return Promise.allSettled(promises).then(resolve);
    });
  }, locationUrls);

  const data = results.filter((res) => res.status === 'fulfilled');
  const failedUrls = results.filter((res) => res.status === 'rejected').map((el) => el.reason);

  locations.push(...data);

  if (failedUrls.length && currentAttempts <= maxAttempts) {
    currentAttempts++;
    return fetchLocations(page, failedUrls, locations, maxAttempts, currentAttempts);
  } else {
    console.log('-'.repeat(50));
    console.log(`complete scrape with ${locations.length} locations`);
    console.log(`with ${failedUrls.length} failed url(s).`);
    failedUrls.map((url) => console.log(url));

    return locations;
  }
}

async function getLocations(page) {
  const links = await getSiteMapLinks(page);
  const locationUrls = generateLocationUrls(links);
  const locations = await fetchLocations(page, locationUrls);

  const failedUrls = [];
  const pois = locations.map((location) => getLocation(location, failedUrls)).filter((poi) => poi);

  console.log('-'.repeat(50));
  console.log(`complete conversion to ${pois.length} pois.`);
  console.log(`with ${failedUrls.length} failed url(s).`);
  failedUrls
    .filter((value, index, self) => self.indexOf(value) === index)
    .map((url) => console.log(url));
  console.log('-'.repeat(50));

  return pois;
}

function getLocation({ value }, failedUrls) {
  const { url, data } = value;
  try {
    const { storeNumber, storeName, telephone, storeOpen, storeClose, addresses } = data;

    const [friendly, physical] = addresses;

    const poi = {
      locator_domain: 'wawa.com',
      page_url: url,
      location_name: getOrDefault(storeName),
      store_number: getOrDefault(storeNumber),
      street_address: getOrDefault(friendly.address),
      city: getOrDefault(friendly.city),
      state: getOrDefault(friendly.state),
      zip: getOrDefault(friendly.zip),
      country_code: 'US',
      latitude: physical.loc[0],
      longitude: physical.loc[1],
      phone: getOrDefault(formatPhone(telephone)),
      hours_of_operation: getOrDefault(formatHoursOfOperation(storeOpen, storeClose)),
      location_type: MISSING,
    };

    return poi;
  } catch (ex) {
    failedUrls.push(url);
    return null;
  }
}

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.wawa.com/site-map',
  });

  const proxyPassword = process.env.APIFY_PROXY_PASSWORD;
  const proxyConfiguration = await Apify.createProxyConfiguration({
    groups: ['RESIDENTIAL'], // List of Apify Proxy groups
    countryCode: 'US',
    password: proxyPassword,
  });

  const launchPuppeteerOptions = {
    useChrome: true,
    stealth: true,
    headless: true,
  };

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    useSessionPool: false,
    persistCookiesPerSession: false,
    maxRequestsPerCrawl: 1,
    maxRequestRetries: 1,
    proxyConfiguration,
    launchPuppeteerOptions,
    handlePageTimeoutSecs: 10 * 60,
    prepareRequestFunction({ request }) {
      request.headers = DEFAULT_HEADERS;
      return request;
    },
    async handlePageFunction({ page }) {
      const locations = await getLocations(page);
      await Apify.pushData(locations);
    },
  });

  await crawler.run();
});
