const Apify = require('apify');
const MISSING = '<MISSING>';

function extractLocatorDomain(url) {
  const domain = url.match(/\/\/(.*?)\//)[1];
  return domain;
}

function extractAddress(address) {
  const components = address.split(', ');

  const zip = components.pop();
  const city = components.pop();
  const street_address = components.join(', ');
  const country_code = 'US';

  return { street_address, city, zip, country_code };
}

async function enqueueLocationLinks({ $, requestQueue }) {
  const locations = $('.location-item');

  console.log(
    locations.map(async (index, dom) => {
      const location = $(dom);
      const btn = location.find('.btn');
      if (!btn.length) return;

      const url = btn.attr('href');
      const location_name = location.find('h3').text();
      const address = location
        .find('p')
        .text()
        .replace(/\s*\r\n/, ', ');
      const phone = $(location.find('a')[0]).text();

      let contactUrl = url;
      contactUrl += url.match(/\/en/) ? 'contact' : 'en/contact';

      return requestQueue.addRequest({
        url: contactUrl,
        userData: {
          location_name,
          address,
          phone,
        },
      });
    })
  );

  await Promise.all(
    locations.toArray().map(async (index, dom) => {
      const location = $(dom);
      const btn = location.find('.btn');
      if (!btn.length) return;

      const url = btn.attr('href');
      const location_name = location.find('h3').text();
      const address = location
        .find('p')
        .text()
        .replace(/\s*\r\n/, ', ');
      const phone = $(location.find('a')[0]).text();

      let contactUrl = url;
      contactUrl += url.match(/\/en/) ? 'contact' : 'en/contact';

      return requestQueue.addRequest({
        url: contactUrl,
        userData: {
          location_name,
          address,
          phone,
        },
      });
    })
  );
}

async function extractDataFromPage({ $, request }) {
  const locator_domain = 'tumbles.net';
  const location_type = 'tumbles';
  const page_url = extractLocatorDomain(request.url);

  const { location_name, phone } = request.userData;
  const [city, state] = location_name.split(', ');
  const address = $('.address span').text();
  const { street_address, zip, country_code } = extractAddress(address);

  return {
    locator_domain,
    page_url,
    location_name,
    location_type,
    street_address,
    city,
    state,
    zip,
    country_code,
    phone,
    hours_of_operation: MISSING,
    store_number: MISSING,
    latitude: MISSING,
    longitude: MISSING,
  };
}

Apify.main(async () => {
  const LOCATIONS_URL = `https://tumbles.net/locations/`;

  const requestQueue = await Apify.openRequestQueue();
  requestQueue.addRequest({
    url: LOCATIONS_URL,
    userData: {
      pageType: 'locations',
    },
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    async handlePageFunction({ $, request }) {
      switch (request.userData.pageType) {
        case 'locations':
          return await enqueueLocationLinks({ $, requestQueue });
        default:
          await Apify.pushData(await extractDataFromPage({ $, request }));
      }
    },
  });

  await crawler.run();
});
