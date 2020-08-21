const Apify = require('apify');
const cheerio = require('cheerio');
const { utils } = Apify;

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

function parseHtml(html) {
  const $ = cheerio.load(html);
  return {
    $,
    getTextByItemProp(name) {
      return $(`[itemprop="${name}"]`).text().trim();
    },
  };
}

function formatPhone(phone) {
  return phone ? phone.replace(/\-|\(|\)|\s/g, '') : null;
}

function enqueueStoreLinks({ page, requestQueue }) {
  return utils.enqueueLinks({
    page,
    requestQueue,
    selector: 'a.brand-item-link',
  });
}

function extractHoursOfOperation($) {
  const rows = $('#open_hour tr');
  const hours = {};
  const data = rows.each(function () {
    const row = $(this);
    const day = row.find('td:nth-child(1)').text().replace(':', '').trim();
    const time = row.find('td:nth-child(2)').text().trim();
    hours[day] = time;
  });
  return JSON.stringify(hours);
}

async function fetchData({ page, request }) {
  // waiting for google popup to load. Sometimes it stalls so just kick it back into queue
  await page.waitForSelector('.store-item', { timeout: 10000 });

  const html = await page.content();
  const parser = parseHtml(html);
  const storePopup = parser.$('.store-item');

  const location_name = parser.getTextByItemProp('name');
  const street_address = parser.getTextByItemProp('streetAddress').split(', ').shift(); // some page include city/state/zip in the address
  const city = parser.getTextByItemProp('addressLocality');
  const state = parser.getTextByItemProp('addressRegion');
  const country_code = parser.getTextByItemProp('addressCountry');
  const latitude = storePopup.attr('data-latitude');
  const longitude = storePopup.attr('data-longitude');
  const store_number = storePopup.attr('data-store-id');
  const phone = formatPhone(parser.getTextByItemProp('telephone'));
  const hours_of_operation = extractHoursOfOperation(parser.$);

  // there are online stores or one that does not exsits
  if (location_name.match(/store\s\d|online/i)) {
    return null;
  }

  return {
    locator_domain: 'shiekh.com',
    page_url: request.url,
    location_name: getOrDefault(location_name),
    street_address: getOrDefault(street_address),
    city: getOrDefault(city),
    state: getOrDefault(state),
    zip: MISSING,
    country_code: getOrDefault(country_code),
    latitude: getOrDefault(latitude),
    longitude: getOrDefault(longitude),
    phone: getOrDefault(phone),
    store_number: getOrDefault(store_number),
    hours_of_operation: getOrDefault(hours_of_operation),
    location_type: MISSING,
  };
}

Apify.main(async function () {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.shiekh.com/store-list',
    userData: {
      pageType: 'locations',
    },
  });

  const proxyPassword = process.env.PROXY_PASSWORD;
  const proxyConfiguration = await Apify.createProxyConfiguration({
    groups: ['RESIDENTIAL'], // List of Apify Proxy groups
    countryCode: 'US',
    password: proxyPassword,
  });

  const puppeteerPoolOptions = {
    retireInstanceAfterRequestCount: 1,
  };

  const launchPuppeteerOptions = {
    headless: true,
    stealth: true,
    useChrome: true,
    useApifyProxy: !!proxyPassword,
    ignoreHTTPSErrors: true,
  };

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    proxyConfiguration,
    puppeteerPoolOptions,
    launchPuppeteerOptions,
    useSessionPool: true,
    maxRequestRetries: 5,
    maxConcurrency: 10,
    maxRequestsPerCrawl: 1000,
    async handlePageFunction({ page, request }) {
      switch (request.userData.pageType) {
        case 'locations':
          await enqueueStoreLinks({ page, requestQueue });
          break;
        default:
          const poi = await fetchData({ page, request });
          if (poi) {
            await Apify.pushData(poi);
          }
      }
    },
  });

  await crawler.run();
});
