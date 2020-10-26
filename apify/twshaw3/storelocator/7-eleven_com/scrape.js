const Apify = require('apify');
const axios = require('axios');

function convertBlank(x) {
  if (!x || (typeof(x) == 'string' && !x.trim())) {
    return "<MISSING>";
  } else {
    return x;
  }
}

function parseHours(json) {
	if (json && json.message && !json.operating) {
		return json.message;
	} else if (json && 'operating' in json && json.operating) {
		hours = []
		for (const day of json.operating) {
			const dayName = day.key;
			const range = day.detail;
			hours.push(`${dayName}: ${range}`);
		}
		return hours.join(', ');
	} else {
		return '<MISSING>';
	}
}

async function scrape() {
  stores = []

  const initialPage = await axios.get('https://www.7-eleven.com/locator');
  const found = initialPage.data.match(/"access_token":"(\w+?)"/);
  let accessToken = null;
  if (found) {
    accessToken = found[1];
  }
  if (!accessToken) {
    console.log('Could not get auth token. Cannot proceed.')
    process.exit(1);
  }
  const HEADERS = {
    'Authorization': `Bearer ${accessToken}`,
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36',
		'Host': 'api.7-eleven.com',
		'Origin': 'https://www.7-eleven.com',
		'Referer': 'https://www.7-eleven.com/',
		'Accept': 'application/json, text/plain, */*',
	}

	let url = 'https://api.7-eleven.com/v4/stores?lat=37.76182419999999&lon=-122.3985871&radius=10000&curr_lat=37.76182419999999&curr_lon=-122.3985871&limit=500&features=' 
	while (url) {
		console.log(url)
		const res = await axios.get(url, { headers: HEADERS });
		const data = res.data;
		url = data.next
		for (let store of data.results) {
			stores.push({
				locator_domain: '7-eleven.com',
				page_url: convertBlank(store.seo_web_url),
				location_name: convertBlank(store.name),
				street_address: convertBlank(store.address),
				city: convertBlank(store.city),
				state: convertBlank(store.state),
				zip: convertBlank(store.zip),
				country_code: convertBlank(store.country),
				store_number: convertBlank(store.id),
				phone: store.phone,
				location_type: '<MISSING>',
				latitude: convertBlank(store.lat),
				longitude: convertBlank(store.lon),
				hours_of_operation: parseHours(store.hours),
			});
		}
	}
	return stores;
}

Apify.main(async () => {
	const data = await scrape();
	await Apify.pushData(data);
});

