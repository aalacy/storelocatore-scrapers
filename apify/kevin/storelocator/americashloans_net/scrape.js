const Apify = require('apify');

function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}

const sleep = async () => {
  const ms = randomIntFromInterval(1000, 5000);
  console.log('sleeping ' + ms + 'ms');
  return Apify.utils.sleep(ms);
};

const handleCities = async ({ request, page, requestQueue, userAgent }) => {
  console.log(`Got ${request.url}`);

  const content = await page.content();
  const storeLinks = await page.evaluate(() => {
    const anchors = Array.from(document.querySelectorAll('div#locations li a'));
    const links = anchors.map(a => ({ name: a.textContent, url: a.href }));
    return links;
  });

  storeLinks.forEach(async link => {
    await requestQueue.addRequest({
      url: link.url,
      userData: {
        pageType: 'store',
        location: link.name,
      },
    });
  });

  await sleep();
};

const getHours = hours => {
  return hours.reduce((acc, current) => {
    if (current.dayOfWeek) {
      if (acc.length > 0) {
        acc += ', ';
      }
      return `${acc}${current.dayOfWeek} ${current.opens} - ${current.closes}`;
    }
    return acc;
  }, '');
};

const handleStore = async ({ request, page }) => {
  console.log(`Got ${request.url}`);

  const loc = {
    locator_domain: 'americashloans.net',
    location_name: null,
    street_address: null,
    city: null,
    state: null,
    zip: null,
    country_code: null,
    store_number: '<MISSING>',
    phone: null,
    location_type: '<MISSING>',
    latitude: null,
    longitude: null,
    hours_of_operation: '',
  };

  const content = await page.content();

  const schema = await page.evaluate(() => {
    const schemaEl = document.querySelector('.yext-schema-json');
    if (schemaEl) {
      return JSON.parse(schemaEl.textContent);
    }
    return null;
  });

  if (schema) {
    loc.location_name = `${schema.name} - ${request.userData.location}`;
    loc.street_address = schema.address.streetAddress;
    loc.city = schema.address.addressLocality;
    loc.state = schema.address.addressRegion;
    loc.zip = schema.address.postalCode;
    loc.country_code = schema.address.addressCountry;
    loc.phone = schema.telephone;
    loc.latitude = schema.geo.latitude;
    loc.longitude = schema.geo.longitude;
    loc.hours_of_operation = getHours(schema.openingHoursSpecification);
  } else {
    // some pages don't have the schema, so scrape the HTML instead
    await page.waitForSelector('.gm-style-iw', {
      timeout: 120000,
    });

    const addressItems = await page.$$eval('.gm-style-iw div#content span', spans => {
      return spans
        .filter(s => s.dataset.type != null)
        .map(s => ({
          type: s.dataset.type,
          content: s.innerText,
        }));
    });

    addressItems.forEach(item => {
      switch (item.type) {
        case 'lead':
          loc.location_name = item.content;
          break;
        case 'address':
          loc.street_address = item.content;
          break;
        case 'city':
          loc.city = item.content;
          break;
        case 'state':
          loc.state = item.content;
          break;
        case 'zipcode':
          loc.zip = item.content;
          break;
        case 'phone':
          loc.phone = item.content;
        case 'regularhours':
        case 'saturdayhours':
          loc.hours_of_operation += item.content === '' ? item.content : '; ' + item.content;
      }
    });

    loc.latitude = '<MISSING>';
    loc.longitude = '<MISSING>';
  }

  console.log(`Parsed ${loc.location_name}`);
  console.log(loc);

  await Apify.pushData(loc);

  await sleep();
};

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();

  await requestQueue.addRequest({
    url: 'https://americashloans.net/stores-by-state/',
    userData: {
      pageType: 'cities',
    },
  });

  const handlePageFunction = async ({ request, page }) => {
    switch (request.userData.pageType) {
      case 'cities':
        await handleCities({ request, page, requestQueue });
        break;

      case 'store':
        await handleStore({ request, page });
        break;
    }
  };

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction,
    maxConcurrency: 10,
    launchPuppeteerOptions: { headless: true },
  });

  await crawler.run();
});
