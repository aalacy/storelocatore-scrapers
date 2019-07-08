const Apify = require('apify');

const {
  locationObjectSelector,
} = require('./selectors');

const {
  formatObject,
  formatPhoneNumber,
  formatHours,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.metromarket.net/storelocator-sitemap.xml',
    userData: {
      urlType: 'initial',
    },
  });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ request, page }) => {
			if (request.userData.urlType === 'initial') {
				console.log("found initial URL");
				await page.waitForSelector('span', { waitUntil: 'load', timeout: 0 });
				console.log("found a span");
				const urls = await page.$$eval('span', se => se.map(s => s.innerText));
				console.log("grabbed span text");
        const locationUrls = urls.filter(e => e.match(/www.metromarket.net\/stores\/details\//))
					.map(e => ({ url: e, userData: { urlType: 'detail' } }));
				console.log("waitint 5 seconds");
        await page.waitFor(5000);
				/* eslint-disable no-restricted-syntax */
				console.log("adding new requests to queue");
        for await (const url of locationUrls) {
          await requestQueue.addRequest(url);
        }
      }
			if (request.userData.urlType === 'detail') {
				console.log("found a detail page");
				if (await page.$(locationObjectSelector) !== null) {
					console.log("got location object selector");
					await page.waitForSelector(locationObjectSelector, { waitUntil: 'load', timeout: 0 });
					console.log("finished waiting for selector");
					const locationObjectRaw = await page.$eval(locationObjectSelector, s => s.innerText);
					console.log("finished getting selector text");
          const locationObject = formatObject(locationObjectRaw);

          const poiData = {
            locator_domain: 'metromarket.net',
            location_name: locationObject.name,
            street_address: locationObject.address.streetAddress,
            city: locationObject.address.addressLocality,
            state: locationObject.address.addressRegion,
            zip: locationObject.address.postalCode,
            country_code: undefined,
            store_number: undefined,
            phone: formatPhoneNumber(locationObject.telephone),
            location_type: locationObject['@type'],
            latitude: locationObject.geo.latitude,
            longitude: locationObject.geo.longitude,
            hours_of_operation: formatHours(locationObject.openingHours),
          };
					const poi = new Poi(poiData);
					console.log("pushing record");
          await Apify.pushData(poi);
          await page.waitFor(5000);
				} else {
					console.log("fetching next request");
          await requestQueue.fetchNextRequest();
        }
      }
    },
    maxRequestsPerCrawl: 100,
    maxConcurrency: 5,
    launchPuppeteerOptions: {
			headless: true,
			stealth: true
		}
  });

  await crawler.run();
});
