const Apify = require('apify');

Apify.main(async () => {

  // console.log('env', Apify.getEnv());

  const requestQueue = await Apify.openRequestQueue();

  await requestQueue.addRequest({
    url: 'http://totalpet.ca/store-locator/',
    userData: {
      pageType: 'html'
    }
  });
  await requestQueue.addRequest({
    url: 'http://totalpet.ca/wp-admin/admin-ajax.php?action=store_search&lat=56.130366&lng=-106.34677099999999&max_results=50&search_radius=1000000&autoload=1',
    userData: {
      pageType: 'json'
    }
  });

  const launchPuppeteerOptions = {
    headless: true,
    stealth: true,
    useChrome: true,
    useApifyProxy: true,
    groups: ['RESIDENTIAL']
  };

  const puppeteerPoolOptions = {
    retireInstanceAfterRequestCount: 1
  }

  const crawler = new Apify.PuppeteerCrawler({
    launchPuppeteerOptions,
    puppeteerPoolOptions,
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

  switch (request.userData.pageType) {
    case 'json':
      const jsonString = await page.evaluate(() => {
        const pre = document.querySelector('pre');
        if (pre) {
          return pre.textContent;
        }
        return {};
      });
      const data = JSON.parse(jsonString);
      // console.log(data);

      data.forEach(async location => {
        const locationName = location.store;

        // open the stored key/value item with hours and phone
        const key = locationName.replace(/\s/g, '-').toLowerCase();
        const storedValue = await Apify.getValue(key);

        const poi = {
          locator_domain: 'totalpet.ca',
          page_url: '<MISSING>',
          location_name: locationName,
          street_address: location.address + (location.address2 ? location.address2 : ""),
          city: location.city,
          state: location.state,
          zip: location.zip,
          country_code: location.country === "Canada" ? "CA" : location.country,
          store_number: location.id,
          phone: storedValue ? storedValue.phone : '<MISSING>',
          location_type: '<MISSING>',
          latitude: location.lat,
          longitude: location.lng,
          hours_of_operation: storedValue ? storedValue.hours : '<MISSING>'
        };

        // console.log(poi);
        await Apify.pushData(poi);
      });

      break;

    case 'html':
      const hours = await page.evaluate(() => {
        return Array
          .from(document.querySelectorAll('section[itemscope="itemscope"]'))
          .reduce((acc, s) => {
            if (s.querySelector('strong')) {
              const data = {}
              data["locName"] = s.querySelector('div > p > span').textContent;
              const phoneP = s.querySelector('div p:first-child');
              data["phone"] = phoneP.lastChild.textContent.trim();
              const hoursP = s.querySelector('div p:nth-child(2)');
              const nonTextNodes = hoursP.querySelectorAll('strong, br');
              nonTextNodes.forEach(n => hoursP.removeChild(n));
              data["hours"] = Array
                .from(hoursP.childNodes)
                .map(n => n.textContent.trim()).join(', ');
              acc.push(data);
            }
            return acc;
          }, []);
      });

      // save to Apify key/value store
      hours.forEach(async h => {
        const key = h.locName.replace(/\s/g, '-').toLowerCase();
        await Apify.setValue(key, h);
      });
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

