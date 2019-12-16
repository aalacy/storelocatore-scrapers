const Apify = require('apify');
const axios = require('axios');

async function scrape() {
	stores = []
	let res = await axios.get('https://momentfeed-prod.apigee.net/api/llp.json?auth_token=GTKDWXDZMLHWYIKP&pageSize=9999999');
	let data = res.data;
	for(let store of data){
		let s = {
			locator_domain: 'https://momentfeed-prod.apigee.net/',
			page_url: store.store_info.website,
			location_name: store.store_info.name,
			street_address: store.store_info.address,
			city: store.store_info.locality,
			state: store.store_info.region,
			zip: store.store_info.postcode,
			country_code: store.store_info.country,
			store_number: store.store_info.corporate_id,
			phone: store.store_info.phone,
			location_type: '<MISSING>',
			latitude: store.store_info.latitude,
			longitude: store.store_info.longitude,
			hours_of_operation: formatHours(store.store_info.hours),
		}
		stores.push(s);
	}
	return stores;
}

function formatHours(hours) {
	const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
	let res = [];
	for (hour of hours.split(';')) {
		const parts = hour.split(',');
		if (parts.length == 3) {
			const day = parseInt(parts[0]) - 1;
			const dayName = days[day];
			const open = parts[1];
			const close = parts[2];
			res.push(dayName + ': ' + open + '-' + close)
		}
	}
	return res.join(', ');
}

Apify.main(async () => {
	const data = await scrape();
	await Apify.pushData(data);
});

