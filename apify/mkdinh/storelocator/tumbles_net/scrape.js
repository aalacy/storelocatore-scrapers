const Apify = require('apify');
const { enqueueLinks } = require('apify').utils;

const MISSING = '<MISSING>';

function extractLocatorDomain(url) {
  [matched, domain] = url.match(/\/\/(.*?)\//);
  return domain;
}

function extractAddress(address) {
  const components = address.split(', ');

  const zip = components.pop();
  const state = components.pop();
  const city = components.pop();
  const street_address = components.join(', ');
  const country_code = 'US';

  return { street_address, city, state, zip, country_code };
}

function extractHoursOfOperation(hours, $) {
  return hours
    .text()
    .replace(/(.*?\S)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/gi, '$1 $2 ')
    .replace(/(\s+\.\s+)|\s+/g, ' ')
    .trim();
}

function extractPhoneNumber(phoneNumber) {
  return phoneNumber.text().replace(/\(|\)|-|\s/g, '');
}

async function enqueueLocationLinks({ $, requestQueue }) {
  return enqueueLinks({
    $,
    requestQueue,
    selector: '.btn',
    baseUrl: 'https://tumbles.net',
    pseudoUrls: ['https://[.*].tumbles.net/'],
  });
}

async function extractDataFromPage({ $, request }) {
  const locator_domain = 'tumbles.net';
  const location_type = 'tumbles';
  const page_url = extractLocatorDomain(request.url);
  const detailsComponent = $('address');
  const location_name = detailsComponent.find('p:nth-child(1)').text();
  const address = detailsComponent.find('p:nth-child(2)').text();
  const { street_address, city, state, zip, country_code } = extractAddress(address);
  const hours = $('.opening-hours ul');
  const hours_of_operation = extractHoursOfOperation(hours, $);

  const phoneNumber = detailsComponent.find('p:nth-child(3) a');
  const phone = extractPhoneNumber(phoneNumber);

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
    hours_of_operation,
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
          const poi = await extractDataFromPage({ $, request });
          await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();
});
