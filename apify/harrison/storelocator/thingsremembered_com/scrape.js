const Apify = require('apify');

Apify.main(async () => {
	const requestQueue = await Apify.openRequestQueue();
	await requestQueue.addRequest({ url: 'https://www.thingsremembered.com/storelocator/stores.json' });

	const useProxy = process.env.USE_PROXY;

	const formatHours = (rawHours) => {
		const days = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
		const parts = rawHours.split('|');
		const hoursForDay = [];
		for (part of parts) {
			const dayParts = part.split("#");
			const dayIndex = parseInt(dayParts[0]);
			const openTime = dayParts[1];
			const closeTime = dayParts[2];
			hoursForDay.push(days[dayIndex - 1] + ": " + openTime + "-" + closeTime);
		}
		return hoursForDay.join(', ');
	}	

	const parseJson = (data) => {
		stores = [];
		for(let store of data) {
			stores.push({
				locator_domain: 'https://www.thingsremembered.com/',
				page_url: '<MISSING>',
				location_name: store.name,
				street_address: store.address1,
				city: store.city,
				state: store.stateAddress,
				zip: store.postalCode,
				country_code: store.country == "USA" ? "US" : store.country,
				store_number: store.locationId,
				phone: store.phoneNumber,
				location_type: '<MISSING>',
				latitude: store.latitude,
				longitude: store.longitude,
				hours_of_operation: formatHours(store.hours),
			});
		}
		return stores;
	}

	const crawler = new Apify.PuppeteerCrawler({
		requestQueue,
		handlePageFunction: async ({ request, page }) => {
			const jsonElement = (await page.$x('//pre'))[0];
			const content = await page.evaluate(x => x.textContent, jsonElement);
			const parsed = parseJson(JSON.parse(content));
			await Apify.pushData(parsed);
		},
		maxRequestsPerCrawl: 100,
		maxConcurrency: 10,
		launchPuppeteerOptions: {headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy},
	});

	await crawler.run();
});

