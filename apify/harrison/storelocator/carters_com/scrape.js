const Apify = require('apify');

Apify.main(async () => {
	const requestQueue = await Apify.openRequestQueue();
	await requestQueue.addRequest({ url: 'https://www.carters.com/on/demandware.store/Sites-Carters-Site/default/Stores-GetNearestStores?carters=true&oshkosh=false&skiphop=false&lat=0&lng=0' });

	const useProxy = process.env.USE_PROXY;

	let stores = [];

	const crawler = new Apify.PuppeteerCrawler({
		requestQueue,
		handlePageFunction: async ({ request, page }) => {

			try {
				let body = await page.evaluate(() => document.body.innerHTML);
				let data = [];
				let capture = false;
				for (line of body.split(/\r?\n/)) {
					if (line.includes('"stores":')) {
						capture = true;
					} else if (line.includes("</pre>")) {
						capture = false;
					}
					if (capture && line.trim()) {
						data.push(line.trim());
					}
				}
				const rawJson = data.join('\n');
				const parsed = JSON.parse(rawJson).stores;
				for(let key in parsed){
					if(parsed[key].isOpen == 'open'){
						let store = parsed[key];
						stores.push({
							locator_domain: 'https://www.carters.com/',
							page_url: '<MISSING>',
							location_name: store.name,
							street_address: store.address1,
							city: store.city,
							state: store.stateCode,
							zip: store.postalCode,
							country_code: store.countryCode,
							store_number: store.storeid,
							phone: store.phone,
							location_type: '<MISSING>',
							latitude: store.latitude,
							longitude: store.longitude,
							hours_of_operation: {
								'Sunday Hours': store.sundayHours,
								'Monday Hours': store.mondayHours,
								'Tuesday Hours': store.tuesdayHours,
								'Wednesday Hours': store.wednesdayHours,
								'Thurday Hours': store.thursdayHours,
								'Friday Hours': store.fridayHours,
								'Saturday Hours': store.saturdayHours,
							},
						});
					}
				}
			} catch(err) {
				console.log(err);
				console.log('Try again later, encountered CAPTCH.');
			}

		},
		maxRequestsPerCrawl: 100,
		maxConcurrency: 10,
		launchPuppeteerOptions: {headless: true, stealth: true, useChrome: true, useApifyProxy: !!useProxy},
	});

	await crawler.run();
	await Apify.pushData(stores);
});
