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

const parseJsonResponse = async (page) => {
  const content = await page.content(); 
  const json = await page.evaluate(() => JSON.parse(document.querySelector("body").innerText)); 
  return json;
}

const formatHours = (hours) => {
  const formattedDays = hours.weekDayOpeningList.map(day => {
    let formatted = '';
    formatted = `${day.weekDay}: `;
    if (day.closed) { 
      formatted += 'Closed';
    } else {
      formatted += `${day.openingTime.formattedHour} - ${day.closingTime.formattedHour}`;
    }
    return formatted;
  });
  return formattedDays.join(', ')
}

const parseLocation = (store) => {
  const location = {
    locator_domain: 'americastire.com',
    location_name: store.displayName,
    street_address: store.address.line1,
    city: store.address.town,
    state: store.address.region.isocodeShort,
    zip: store.address.postalCode,
    country_code: store.address.country.isocode,
    store_number: store.legacyStoreCode,
    phone: store.address.phone,
    location_type: store.type,
    latitude: store.geoPoint.latitude,
    longitude: store.geoPoint.longitude,
    hours_of_operation: formatHours(store.openingHours)
  };
  return location;
}

const handleCitySearch = async ({request, page, requestQueue, userAgent}) => {

  console.log(`Got ${request.url}`);

  const jsonCities = await parseJsonResponse(page);

  console.log(`Cities for ${request.userData.state}`);

  jsonCities.forEach(async city => {

    console.log(`${city.name} (${city.storeCount})`);

    const formattedState = request.userData.state.replace(' ', '%20');
    const formattedCity = city.name.replace(' ', '%20');

    await requestQueue.addRequest({ 
      url: `https://www.americastire.com/store-locator/findStores?q=${formattedCity},${formattedState}&max=75&searchByCity=true`,
      headers: {
        'user-agent': userAgent, 
        accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,la;q=0.8'
      },
      userData: {
        pageType: 'stores', 
        city: city.name
      }
    });

  });

  await sleep();

}

const handleStoreSearch = async ({request, page}) => {

  console.log(`Got ${request.url}`);

  const jsonStores = await parseJsonResponse(page);

  console.log(`Stores for ${request.userData.city}`);

  jsonStores.results.forEach(async store => {

    const location = parseLocation(store);
    console.log(location.location_name);
    await Apify.pushData(location);

  });

}


Apify.main(async () => {

  const userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' + 
    ' Chrome/75.0.3770.100 Safari/537.36'
  
  const states = [
    'Alabama','Alaska','Arizona','Arkansas',
    'California','Colorado','Connecticut','Delaware',
    'Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa',
    'Kansas','Kentucky','Louisiana',
    'Maine','Maryland','Massachusetts',
    'Michigan','Minnesota','Mississippi','Missouri','Montana',
    'Nebraska','Nevada','New Hampshire','New Jersey','New Mexico',
    'New York','North Carolina','North Dakota',
    'Ohio','Oklahoma','Oregon','Pennsylvania',
    'Rhode Island','South Carolina','South Dakota','Tennessee',
    'Texas','Utah','Vermont','Virginia','Washington',
    'West Virginia','Wisconsin','Wyoming'
  ];

  const requestQueue = await Apify.openRequestQueue();

  // queue up a search for cities within each state
  states.forEach(async (state) => {
    const formattedState = state.replace(' ', '%20');
    await requestQueue.addRequest({ 
      url: `https://www.americastire.com/store-locator/storeCount/${formattedState}`,
      headers: {
        'user-agent': userAgent, 
        accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,la;q=0.8'
      },
      userData: {
        pageType: 'cities', 
        state
      }
    });
  });

  const handlePageFunction = async ({ request, page }) => {

    switch (request.userData.pageType) {

      case 'cities':
        await handleCitySearch({request, page, requestQueue, userAgent});
        break;

      case 'stores': 
        await handleStoreSearch({request, page, userAgent});
        break;
    } 

  };

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
		handlePageFunction,
		maxConcurrency: 5,
		launchPuppeteerOptions: {headless: true},
  });

  await crawler.run();
});
