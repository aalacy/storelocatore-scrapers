const Apify = require('apify');
const axios = require('axios');

function convertBlank(x) {
  if (!x || (typeof(x) == 'string' && !x.trim())) {
    return "<MISSING>";
  } else {
    return x;
  }
}

async function scrape() {
	stores = []
	let res = await axios.get('https://columbia.locally.com/stores/conversion_data');
	for (let store of res.data.markers) {
		if (store.company_id == 67) {
			let s = {
				locator_domain: 'https://www.columbia.com/',
				page_url: '<MISSING>',
				location_name: convertBlank(store.name),
				street_address: convertBlank(store.address),
				city: convertBlank(store.city),
				state: convertBlank(store.state),
				zip: convertBlank(store.zip),
				country_code: convertBlank(store.country),
				store_number: convertBlank(store.id),
				phone: convertBlank(store.phone),
				location_type: '<MISSING>',
				latitude: convertBlank(store.lat),
				longitude: convertBlank(store.lng),
				hours_of_operation: '<MISSING>'
			}
			if(store.sun_time_open != 0 && store.mon_time_open != 0
				&& store.wed_time_open != 0 && store.fri_time_open != 0){
				s.hours_of_operation = {
					sun_time_open: store.sun_time_open,
					sun_time_close: store.sun_time_close,
					mon_time_open: store.mon_time_open,
					mon_time_close: store.mon_time_close,
					tue_time_open: store.tue_time_open,
					tue_time_close: store.tue_time_close,
					wed_time_open: store.wed_time_open,
					wed_time_close: store.wed_time_close,
					thu_time_open: store.thu_time_open,
					thu_time_close: store.thu_time_close,
					fri_time_open: store.fri_time_open,
					fri_time_close: store.fri_time_close,
					sat_time_open: store.sat_time_open,
					sat_time_close: store.sat_time_close
				}
			}
			stores.push(s);

		}
	}
	return stores;

}

Apify.main(async () => {
	const data = await scrape();
	await Apify.pushData(data);
});

