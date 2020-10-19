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
	
	base_link = "https://www.franzbakery.com/JS/locations.id.json"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	stores = session.get(base_link, headers = HEADERS).json()['features']

	data = []
	
	locator_domain = "franzbakery.com"

	for store in stores:
		if store['properties']['category'] != "Bakery":
			continue	

		link = "<MISSING>"

		street_address = (str(store['properties']['streetNumber']) + " " + store['properties']['street']).strip()
		city = store['properties']['city']
		state = store['properties']['state']
		zip_code = store['properties']['zip']
		country_code = "US"
		store_number = "<MISSING>"
		phone = store['properties']['phone']
		latitude = store['geometry']['coordinates'][1]
		longitude = store['geometry']['coordinates'][0]
		hours_of_operation = "<MISSING>"
		location_type = "<MISSING>"
		location_name = "Franz Bakery - " + city
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
