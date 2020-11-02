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
	let res = await axios.get('https://ocharleys.com/webapi/Locations');
	let data = res.data;
	for(let store of data){
		let s = {
			locator_domain: 'http://ocharleys.com/',
			page_url: convertBlank(store.Website),
			location_name: convertBlank(store.FriendlyName),
			street_address: convertBlank(store.Address),
			city: convertBlank(store.City),
			state: convertBlank(store.State),
			zip: convertBlank(store.Zip),
			country_code: 'US',
			store_number: convertBlank(store.StoreId),
			phone: convertBlank(store.MainPhone),
			location_type: convertBlank(store.CurbsideToGo),
			latitude: convertBlank(store.Latitude),
			longitude: convertBlank(store.Longitude),
			hours_of_operation: {
				'MonOpen': store.MonOpen,
				'MonClose': store.MonClose,
				'TueOpen': store.TueOpen,
				'TueClose': store.TueClose,
				'WedOpen': store.WedOpen,
				'WedClose': store.WedClose,
				'ThuOpen': store.ThuOpen,
				'ThuClose': store.ThuClose,
				'FriOpen': store.FriOpen,
				'FriClose': store.FriClose,
				'SatOpen': store.SatOpen,
				'SatClose': store.SatClose,
				'SunOpen': store.SunOpen,
				'SunClose': store.SunClose
			},
		}
		stores.push(s);
	}
	return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

