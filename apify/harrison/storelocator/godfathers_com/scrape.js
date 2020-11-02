const Apify = require('apify');
const axios = require('axios');

function formatHours(hoursJson) {
	if (!hoursJson) {
		return '<MISSING>';
	}
	days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
	hours = [];
	for (part of hoursJson) {
		if ('monday' in part) {
			for (day of days) {
				open = part[day]['openTime']['timeString'].split(',')[0];
				close = part[day]['closeTime']['timeString'].split(',')[0];
				hours.push(`${day}: ${open} - ${close}`);
			}
		}
		return hours.join(', ');
	}
	return '<MISSING>';
}

async function scrape() {
	stores = []
	let res = await axios.get('https://api-prod-gfp-us-a.tillster.com/mobilem8-web-service/rest/storeinfo/distance?_=1559334498038&latitude=0&longitude=0&maxResults=999999&radius=999999&statuses=ACTIVE,TEMP-INACTIVE,ORDERING-DISABLED&tenant=gfp-us');
	for (let store of res.data.getStoresResult.stores) {
		zipCode = store.zipCode.toString();
		if (zipCode.length < 5) zipCode = '<MISSING>';
		phoneNumber = store.phoneNumber;
		if (!phoneNumber) phoneNumber = '<MISSING>';
		phoneNumber = phoneNumber.toString();
		if (phoneNumber.includes(' or ')) phoneNumber = phoneNumber.split(' or ')[0];
		else if (phoneNumber.replace(/[^0-9]/g,"").length != 10) phoneNumber = '<MISSING>';
		stores.push({
			locator_domain: 'godfathers.com',
			page_url: '<MISSING>',
			location_name: store.storeName,
			street_address: store.street,
			city: store.city,
			state: store.state == 'Davidson' ? '<MISSING>' : store.state,
			zip: zipCode,
			country_code: store.country,
			store_number: store.storeName.split('-')[1],
			phone: phoneNumber,
			location_type: '<MISSING>',
			latitude: store.latitude == "0E-8" ? "<MISSING>" : store.latitude,
			longitude: store.longitude == "0E-8" ? "<MISSING>" : store.longitude,
			hours_of_operation: formatHours(store.storeHours)
		});
	}
	return stores;

}

Apify.main(async () => {
	const data = await scrape();
	await Apify.pushData(data);
});

