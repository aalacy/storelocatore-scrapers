const Apify = require('apify');
const cheerio = require('cheerio');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

function get(key, object) {
  return getOrDefault(object[key]);
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
  return phone ? phone.replace(/-|\(|\)|\s/g, '') : null;
}

async function enqueueStoreLinks({ page, requestQueue, request }) {
  const { locations, curPage } = request.userData;

  const content = await page.content();
  const $ = cheerio.load(content);
  const serialized = $('pre').html();

  const { num_store, storesjson } = JSON.parse(serialized.replace(/&quot;/g, '"'));

  locations.push(...storesjson);

  if (locations.length < num_store) {
    const nextPage = curPage + 1;

    await requestQueue.addRequest({
      url: `https://www.shiekh.com/storelocator/index/loadstore?curPage=${nextPage}`,
      userData: {
        locations,
        curPage: nextPage,
        pageType: 'locations',
      },
    });
  } else {
    await Promise.all(
      locations.map((loc) =>
        requestQueue.addRequest({
          url: `https://www.shiekhshoes.com/${loc.rewrite_request_path}`,
          userData: {
            location: loc,
          },
        })
      )
    );
  }
}

function extractHoursOfOperation($) {
  const rows = $('#open_hour tr');
  const hours = [];
  rows.each(function () {
    const row = $(this);
    const day = row.find('td:nth-child(1)').text().replace(':', '').trim();
    const time = row.find('td:nth-child(2)').text().trim();
    hours.push(`${day}: ${time}`);
  });
  return hours.join(',');
}

async function fetchData({ page, request }) {
  const html = await page.content();
  const parser = parseHtml(html);
  const storePopup = parser.$('.store-item');
  const { location } = request.userData;

  const location_name = parser.getTextByItemProp('name') || get('store_name', location);
  const street_address =
    parser.getTextByItemProp('streetAddress').split(', ').shift() || get('address', location); // some page include city/state/zip in the address
  const city = parser.getTextByItemProp('addressLocality');
  const state = parser.getTextByItemProp('addressRegion');
  const country_code = parser.getTextByItemProp('addressCountry');
  const latitude = storePopup.attr('data-latitude') || get('latitude', location);
  const longitude = storePopup.attr('data-longituk4worde') || get('longitude', location);
  const store_number = storePopup.attr('data-store-id') || get('storelocator_id', location);
  const phone =
    formatPhone(parser.getTextByItemProp('telephone')) || formatPhone(get('phone', location));
  const hours_of_operation = extractHoursOfOperation(parser.$);

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
    record_id: 'store_number',
  };
}

Apify.main(async function () {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.shiekh.com/storelocator/index/loadstore/',
    userData: {
      curPage: 1,
      pageType: 'locations',
      locations: [],
    },
  });
  5;
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
    maxRequestRetries: 10,
    maxConcurrency: 1,
    maxRequestsPerCrawl: 1000,
    async handlePageFunction({ page, request }) {
      switch (request.userData.pageType) {
        case 'locations': {
          await enqueueStoreLinks({ page, requestQueue, request });
          break;
        }
        default: {
          const poi = await fetchData({ page, request });
          if (poi) {
            await Apify.pushData(poi);
          }
        }
      }
    },
  });

  await crawler.run();
});
