const Apify = require('apify');

Apify.main(async () => {

	const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ 
    url: 'https://www.foxrentacar.com/en/locations.html',
    userData: {
      pageType: 'locations'
    }
  });
  
  const launchPuppeteerOptions = {
    headless: true,
    stealth: true,
    useChrome: true
  };

  const proxyPassword = process.env.PROXY_PASSWORD;
  if (proxyPassword) {
    const proxyUserName = 'groups-RESIDENTIAL,country-us';
    const proxyUrl = `http://${proxyUserName}:${proxyPassword}@proxy.apify.com:8000`;
    launchPuppeteerOptions.proxyUrl = proxyUrl;
  }
  
	const crawler = new Apify.PuppeteerCrawler({
    launchPuppeteerOptions,
    maxRequestsPerCrawl: 100,
    maxConcurrency: 1,
    requestQueue,
		handlePageFunction: handlePageFunction.bind(null, requestQueue),
    handleFailedRequestFunction
	});

  await crawler.run();
  
});


async function handlePageFunction(requestQueue, { request, page }) {

  switch (request.userData.pageType) {
    case 'locations':
      await getLocations({ page, requestQueue });
      break;

    case 'locationDetail':
      await getLocationDetail(page)
      break;
  }

}


async function handleFailedRequestFunction({ request }) {
  // This function is called if the page processing failed more than maxRequestRetries+1 times.
  console.log(`Request ${request.url} failed too many times`);
  await Apify.pushData({
    '#debug': Apify.utils.createRequestDebugInfo(request),
  });
}


async function getLocations({ page, requestQueue }) {
  await Apify.utils.enqueueLinks({
    page,
    requestQueue,
    selector: 'li.clearfix > a',
    // filter for only u.s. and canada
    pseudoUrls: ['https://www.foxrentacar.com/en/locations/[canada|united-states]/[.+]'],
    transformRequestFunction: request => {
      request.userData.pageType = 'locationDetail';
      return request;
    }
  });
}


async function getLocationDetail(page) {

  const address = await getAddress(page);

  const poi = {
    locator_domain: 'foxrentacar.com',
    page_url: page.url(),
    location_name: await page.$eval('div.margin_bottom > div > h3', el => el.textContent),
    street_address: address.street,
    city: address.city,
    state: address.state,
    zip: address.zip,
    country_code: address.country,
    store_number: '<MISSING>',
    phone: await page.$eval('a[href^=tel]', el => el.textContent),
    location_type: '<MISSING>',
    latitude: '<MISSING>',
    longitude: '<MISSING>',
    hours_of_operation: await getHours(page)
  };

  await Apify.pushData([poi]);

}

async function getAddress(page) {

  const address = await page.evaluate(() => {

    function parseCityStateZipCountry(str) {
      const obj = {};

      const parts = str.split(' ');
      const len = parts.length;

      obj.country = parts[len - 1]

      if (obj.country === 'US') {
        obj.zip = parts[len - 2]
        obj.state = parts[len - 3]
        obj.city = parts.slice(0, len - 3).join(' ')
      } else if (obj.country === 'CA') {
        obj.zip = parts.slice(len - 3, len - 1).join(' ');
        obj.state = parts[len - 4];
        obj.city = parts.slice(0, parts.length - 4).join(' ')
      }

      return obj;
    }


    const addressDivs = document.querySelectorAll('div.loc-address h5');
    let streetAddress = addressDivs[0].textContent;
    let cityStateZipCountry;

    switch(addressDivs.length) {
      case 2: 
        cityStateZipCountry = addressDivs[1].textContent;
        break;
      case 3: 
        streetAddress += ", " + addressDivs[1].textContent;
        cityStateZipCountry = addressDivs[2].textContent;
        break;
    }

    const obj = parseCityStateZipCountry(cityStateZipCountry);
    obj.street = streetAddress;

    return obj;
  });

  return address;

}


async function getHours(page) {

  const hours = await page.evaluate(() => {

    const hoursBlockDivs = document.querySelectorAll('div.busines-hours');

    // account for some odd pages with multiple hours blocks, such as:
    //  /en/locations/canada/winnipeg-james-armstrong-richardson-international-airport.html
    let dayDivs = null;
    for (let i = 0; i < hoursBlockDivs.length; i++) {
      const hoursBlock = hoursBlockDivs[i];
      // use the first hours block that has >= 5 days listed
      const childDayDivs = hoursBlock.querySelectorAll('div.row');
      if (!dayDivs && childDayDivs.length >= 5) {
        dayDivs = childDayDivs;
        break;
      }
    }

    const daysHours = Array
      .from(dayDivs)
      .reduce((acc, d) => {
        const nameDiv = d.querySelector('div.text-right');
        if (nameDiv) {
          const valueDiv = nameDiv.nextElementSibling;
          if (valueDiv) {
            acc.push({ day: nameDiv.textContent, hours: valueDiv.textContent });
          }
        };
        return acc;
      }, []);

    const allHours = daysHours.reduce((acc, item) => {
      if (acc.length > 0) { acc += ', '; }
      return `${acc}${item.day} ${item.hours}`;
    }, '');

    return allHours;

  });

  return hours;

}