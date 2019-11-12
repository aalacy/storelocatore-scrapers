const Apify = require('apify');
const axios = require('axios');

const PN_REGEX = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/im;

function convertBlank(x) {
  if (!x || (typeof(x) == 'string' && !x.trim())) {
    return "<MISSING>";
  } else {
    return x;
  }
}

function padZip(z) {
	if (z.length == 4) {
		return '0' + z;
	}
	return z;
}

async function scrape() {
	stores = []
	let res = await axios.get('https://www.burgerim.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=e151aba9dc&load_all=1&layout=1');
	let data = res.data;
	for(let store of data){
		if (store.categories != null){
			const city = convertBlank(store.city);
			const state = convertBlank(store.state);
			const zip = padZip(convertBlank(store.postal_code));
			let phone = convertBlank(store.phone);
			if (!PN_REGEX.test(phone)) phone = '<MISSING>'
			stores.push({
				locator_domain: 'https://www.burgerim.com/',
				page_url: '<MISSING>',
				location_name: convertBlank(store.title),
				street_address: convertBlank(store.street).split(city + ', ' + state)[0],
				city: city,
				state: state,
				zip: zip,
				country_code: 'US',
				store_number: convertBlank(store.id),
				phone: phone,
				location_type: '<MISSING>',
				latitude: convertBlank(store.lat),
				longitude: convertBlank(store.lng),
				hours_of_operation: convertBlank(store.open_hours),
			});
		}
	}
	return stores;
}

Apify.main(async () => {
	const data = await scrape();
	await Apify.pushData(data);
});

