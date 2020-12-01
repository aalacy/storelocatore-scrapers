const Apify = require('apify');
const MISSING = '<MISSING>';
print('hello');
Apify.main(async () => {
  const requestList = await Apify.openRequestList('locations', [
    {
      url: 'https://www.amegybank.com/',
    },
  ]);

  const launchPuppeteerOptions = {
    useChrome: true,
    stealth: true,
    headless: true,
  };

  const crawler = new Apify.PuppeteerCrawler({
    requestList,
    launchPuppeteerOptions,
    maxRequestRetries: 1,
    maxRequestPerCrawl: 1,
    handlePageTimeoutSecs: 10 * 60,
    async handlePageFunction({ page }) {
      const data = await page.evaluate(async (body) => {
        const response = await fetch(
          'https://www.amegybank.com/locationservices/searchwithfilter',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body,
          }
        );
        return await response.json();
      }, JSON.stringify(getRequestData()));

      const locations = data.location.map(getLocation);
      await Apify.pushData(locations);
    },
  });

  await crawler.run();
});

function getLocation(location) {
  return {
    locator_domain: 'amegybank.com',
    location_name: get(location, 'locationName'),
    street_address: get(location, 'address'),
    city: get(location, 'city'),
    state: get(location, 'stateProvince').toUpperCase(),
    zip: get(location, 'postalCode'),
    country_code: get(location, 'country', 'US').toUpperCase(),
    latitude: get(location, 'lat'),
    longitude: get(location, 'long'),
    store_number: get(location, 'locationId'),
    phone: get(location, 'phoneNumber'),
    location_type: getOneOfAttributes(location.locationAttributes, ['Other Services']),
    hours_of_operation: getOneOfAttributes(location.locationAttributes, [
      'Location Hours',
      'Motor Bank Hours',
      'ATM Hours',
    ]),
  };
}

function getRequestData() {
  return {
    channel: 'Online',
    schemaVersion: '1.0',
    transactionId: 'txId',
    affiliate: '0175',
    clientUserId: 'ZIONPUBLICSITE',
    clientApplication: 'ZIONPUBLICSITE',
    username: 'ZIONPUBLICSITE',
    searchAddress: {
      address: 'Texas',
      city: null,
      stateProvince: null,
      postalCode: null,
      country: null,
    },
    searchFilters: [{ fieldId: '1', domainId: '175', displayOrder: 1, groupNumber: 1 }],
    distance: '5000',
    searchResults: '2000',
  };
}

function get(entity, key, defaultValue = MISSING) {
  return entity[key] || defaultValue;
}

function getOneOfAttributes(attributes, keys) {
  for (let key of keys) {
    for (let a of attributes) {
      if (a['name'] == key) {
        return get(a, 'value');
      }
    }
  }

  return MISSING;
}
