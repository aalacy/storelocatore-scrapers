const Apify = require('apify');
const axios = require('axios');

async function scrape() {
	stores = []
	let res = await axios.get('https://locations.pon-bon.com/locations.json');
	let data = res.data.locations;
	for(let store of data){
		s = {
			locator_domain: 'pon-bon.com',
			page_url: 'https://locations.pon-bon.com/' + store.url,
			location_name: convertBlank(store.loc.name),
			street_address: convertBlank(store.loc.address1),
			city: convertBlank(store.loc.city),
			state: convertBlank(store.loc.state),
			zip: convertBlank(store.loc.postalCode),
			country_code: convertBlank(store.loc.country),
			store_number: convertBlank(store.loc.id),
			phone: convertBlank(store.loc.phone),
			location_type: convertBlank(store.loc.type),
			latitude: convertBlank(store.loc.latitude),
			longitude: convertBlank(store.loc.longitude),
			hours_of_operation: parseHours(store.loc.hours.days),
		}
		stores.push(s);
	}
	return stores;
}

function convertBlank(x) {
  if (!x || (typeof(x) == 'string' && !x.trim())) {
    return "<MISSING>";
  } else {
    return x;
  }
}

function parseHours(hours) {
	if (!hours || hours.length == 0) return '<MISSING>';
	let parts = [];
	for (hour of hours) {
		let res = '';
		res += hour.day;
		res += ': '
		if (hour.intervals.length == 0) {
			res += 'closed';
		} else {
			let intervalParts = [];
			for (interval of hour.intervals) {
				intervalParts.push(interval.start + '-' + interval.end);
			}
			res += intervalParts.join(',');
		}
		parts.push(res);
	}
	return parts.join(', ');
}

Apify.main(async () => {
	const data = await scrape();
	await Apify.pushData(data);
});

