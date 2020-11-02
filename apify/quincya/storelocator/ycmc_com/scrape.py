from sgrequests import SgRequests
import csv

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=your-city-my-city.myshopify.com&latitude=38.916271589264916&longitude=-76.965986&max_distance=0&limit=100"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	stores = session.get(base_link, headers = HEADERS).json()['stores']

	data = []
	
	locator_domain = "ycmc.com"

	for store in stores:
		location_name = store['name'].encode("ascii", "replace").decode().replace("?","D").strip()
		link  = store['website']
		if not link:
			link = "<MISSING>"

		street_address = (store['address'].strip() + " " + store['address2']).strip()
		city = store['city']
		state = store['prov_state']
		zip_code = store['postal_zip']
		country_code = "US"

		store_id = store['store_id']
		id_link = "https://stores.boldapps.net/front-end/get_store_info.php?shop=your-city-my-city.myshopify.com&data=detailed&store_id=" + store_id
		store_json = session.get(id_link, headers = HEADERS).json()['data']
		store_number = store_json.split("custom_field_value'>")[-1].split("<")[0]

		phone = store['phone']
		latitude = store['lat']
		longitude = store['lng']

		hours_of_operation = store['hours'].replace("\r\n"," ").strip()
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"
		location_type = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
