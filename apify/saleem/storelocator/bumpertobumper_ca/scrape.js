const Apify = require('apify');
const request = require('request-promise');

const renameKeys = (keysMap, obj) => {
  return Object.keys(obj).reduce((acc, key) => {
    if (!keysMap[key]) {
      return acc
    }
    return {
      ...{ [keysMap[key] || key]: obj[key]},
      ...acc
    }
  },
  {}
  )
}

// store ids are in a range from 1280 to 1429 (non-contiguous)
let i = 1280;
const sources = [];
while (i <= 1429) {
	sources.push({ url: `https://bumpertobumper.ca/en/getInfo/${i}` });
	i++
}

(async() => {
	const requestList = new Apify.RequestList({sources});
  await requestList.initialize();
  const records =[];
  const failedUrls = [];

	const crawler = new Apify.BasicCrawler({
		requestList,
		handleRequestFunction: async ({ request: requestObj }) => {
      await request.get(requestObj.url)
      .then(json => {
        const locationData = JSON.parse(json);
        const keys_map = {
          name: 'location_name',
          address: 'street_address',
          city: 'city',
          province: 'state',
          postal_code: 'zip',
          garage_id: 'store_number',
          phone: 'phone',
          garage_type: 'location_type',
          lat: 'latitude',
          long: 'longitude',
          schedule: 'hours_of_operation',
          locator_domain: 'locator_domain',
          country_code: 'country_code',
        }
        locationData.locator_domain = 'bumpertobumper_ca';
        locationData.country_code = 'CA';
        locationData.schedule = JSON.stringify(locationData.schedule);
        records.push(renameKeys(keys_map, locationData));
      })
      // catch ids in range that don't correspond to a store
      .catch(error => {
        // console.log(`Domain: ${requestObj.url} returned error: ${error}`)
        failedUrls.push(requestObj.url);
      })
    }
	});

  await crawler.run();
  await Apify.pushData(records);
  // console.log("These urls in range don't exist:")
  // console.log(failedUrls);


	// End scraper
})();