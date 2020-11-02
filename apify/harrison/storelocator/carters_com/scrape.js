const Apify = require('apify');

function convertBlank(x) {
	if (!x || (typeof(x) == 'string' && !x.trim())) {
		return "<MISSING>";
	} else {
		return x;
	}
}

Apify.main(async () => {
	const requestQueue = await Apify.openRequestQueue();
	await requestQueue.addRequest({ url: 'https://www.carters.com/on/demandware.store/Sites-Carters-Site/default/Stores-GetNearestStores?carters=true&oshkosh=true&skiphop=false&lat=0&lng=0' });

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
							location_name: convertBlank(store.name),
							street_address: convertBlank(store.address1),
							city: convertBlank(store.city),
							state: convertBlank(store.stateCode),
							zip: convertBlank(store.postalCode),
							country_code: convertBlank(store.countryCode),
							store_number: convertBlank(store.storeid),
							phone: convertBlank(store.phone),
							location_type: convertBlank(store.brand),
							latitude: convertBlank(store.latitude),
							longitude: convertBlank(store.longitude),
							hours_of_operation: JSON.stringify({
								'Sunday': store.sundayHours,
								'Monday': store.mondayHours,
								'Tuesday': store.tuesdayHours,
								'Wednesday': store.wednesdayHours,
								'Thurday': store.thursdayHours,
								'Friday': store.fridayHours,
								'Saturday': store.saturdayHours,
							}),
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
