const Apify = require('apify');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ url: 'https://www.ardene.com/us/en/stores/' });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
		handlePageFunction: async ({ request, page }) => {

			// Being scraper

      data = await page.evaluate("$.ajax({url: $('#google-map').data('updates-url'),data: {'distanceUnit': 'mi','maxDistance': 100000,'lat': '37.09024','lng': '-95.71289100000001','maxStores': 1000000},method: 'post',dataType: 'json',success: function success(response) {return response;}});");
      formatted = [];
      for (let d of data){
        address = 
        formatted.push({
          locator_domain: 'ardene.com',
          location_name: d.name,
          street_address: fixAddress(d.address1 + " " + d.address2),
          city: fixCity(d.city),
          state: fixState(d.stateCode),
          zip: d.postalCode.trim(),
          country_code: d.countryCode,
          store_number: '<MISSING>',
          phone: d.phone,
          location_type: '<MISSING>',
          latitude: d.location.lat,
          longitude: d.location.lng,
          hours_of_operation: d.storeHours,
        });
      }
    
			
			await Apify.pushData(formatted);

			// End scraper

    },
    maxRequestsPerCrawl: 100,
		maxConcurrency: 10,
		launchPuppeteerOptions: {headless: true},
  });

  await crawler.run();
});

function fixAddress(address){
  return address.replace('null', '').trim();
}

function fixCity(city){
  switch(city){
    case 'Massachusetts' : city = 'Boston'; break;
    case null : city = "<MISSING>"; break;
    default: break;
  }
  return city;
}

function fixState(code){
  switch(code)  {
    case 'NF' : code = 'NL'; break;
    case 'BOSTON' : code = 'Massachusetts'; break;
    default: break;
  }
  return code;
}
