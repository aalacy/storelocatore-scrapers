const Apify = require('apify');

Apify.main(async () => {

  const requestQueue = await Apify.openRequestQueue();

  await requestQueue.addRequest({
    url: 'https://tisol.ca/locations/'
  });

  const launchPuppeteerOptions = {
    headless: true,
    stealth: true,
    useChrome: true
  };

  const DEFAULT_PROXY_URL = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"
  const proxyPassword = process.env.PROXY_PASSWORD;
  if (proxyPassword) {
    const proxyUrl = (process.env.PROXY_URL || DEFAULT_PROXY_URL).replace('{}', proxyPassword);
    launchPuppeteerOptions.proxyUrl = proxyUrl;
  }

  const crawler = new Apify.PuppeteerCrawler({
    launchPuppeteerOptions,
    maxRequestsPerCrawl: 100,
    maxConcurrency: 1,
    requestQueue,
    handlePageFunction,
    handleFailedRequestFunction
  });

  await crawler.run();

});


async function handlePageFunction({ request, page }) {
  console.log(`*** Processing ${request.url}...`);

  const locations = await page.evaluate(() => {
    return Array
      .from(document.querySelectorAll('div.et_pb_map_pin'))
      .reduce((acc, s) => {
        const data = {};
        data.name = s.querySelector('h3').textContent;
        const details = s.querySelector('p');
        console.log(details);
        const addressParts = details.firstChild.textContent.split(',');
        data.streetAddress = addressParts[0].trim();
        data.city = addressParts[1].trim();
        data.state = '<MISSING>';
        data.zip = addressParts[2].trim();
        data.phone = details.querySelector('a').textContent;
        data.lat = s.getAttribute('data-lat');
        data.lng = s.getAttribute('data-lng');
        data.url = "https://www.tisol.ca" + s.querySelector('span.loc-more-details a').getAttribute('href');

        const hoursInfo = Array.from(details.childNodes).reduce((acc, n, idx) => {
          if (idx > 0 && n.nodeType === Node.TEXT_NODE || n.nodeName === 'STRONG') {
            acc.push(n.textContent);
          }
          return acc;
        }, []);
        data.hours = `${hoursInfo.slice(0, 3).join('')}, ${hoursInfo.slice(3).join('')}`

        acc.push(data);
        return acc;
      }, []);
  });

  locations.forEach(async location => {
    const poi = {
      locator_domain: 'tisol.ca',
      page_url: location.url,
      location_name: location.name,
      street_address: location.streetAddress,
      city: location.city,
      state: location.state,
      zip: location.zip,
      country_code: "CA",
      store_number: '<MISSING>',
      phone: location.phone,
      location_type: '<MISSING>',
      latitude: location.lat,
      longitude: location.lng,
      hours_of_operation: location.hours
    };

    await Apify.pushData(poi);
  });

}


async function handleFailedRequestFunction({ request }) {
  // This function is called if the page processing failed more than maxRequestRetries+1 times.
  console.log(`Request ${request.url} failed too many times`);
  await Apify.pushData({
    '#debug': Apify.utils.createRequestDebugInfo(request),
  });
}

