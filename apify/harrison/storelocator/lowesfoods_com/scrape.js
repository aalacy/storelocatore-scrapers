const Apify = require('apify');
const axios = require('axios');

async function scrape() {
	stores = []
	let payload = { Latitude: 0.0, Longitude: 0.0, Radius: 100000, SearchByRadius: true }
	let res = await axios.post('https://www.lowesfoods.com/StoreLocator/SearchNearByStores', payload);
	let data = res.data;
	for(const store of data){
		stores.push({
			locator_domain: 'http://www.lowesfoods.com/',
			page_url: 'http://www.lowesfoods.com/' + store.PageUrl, 
			location_name: store.StoreShortName,
			street_address: store.Address1,
			city: store.City,
			state: store.State,
			zip: store.Zipcode,
			country_code: 'US',
			store_number: store.StoreNumber,
			phone: store.Phone,
			location_type: '<MISSING>',
			latitude: store.Latitude,
			longitude: store.Longitude,
			hours_of_operation: store.StoreOpenHours,
		});
	}
	return stores;
}

Apify.main(async () => {
	const data = await scrape();
	await Apify.pushData(data);
});

