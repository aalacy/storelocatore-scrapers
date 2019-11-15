const Apify = require('apify');
const axios = require('axios');

const days = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];

async function scrape() {
	stores = []
	let res = await axios.get('https://www.thingsremembered.com/storelocator/stores.json');
	let data = res.data;
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

function formatHours(rawHours) {
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

Apify.main(async () => {
	const data = await scrape();
	await Apify.pushData(data);
});

