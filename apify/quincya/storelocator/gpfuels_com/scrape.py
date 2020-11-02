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
	
	base_link = 'http://www.gpfuels.com/maps/geojson/layer/1/?full=no&full_icon_url=no&listmarkers=1'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	stores = session.get(base_link, headers = HEADERS).json()['features']

	data = []
	locator_domain = "gpfuels.com"

	for store in stores:
		location_name = store["properties"]["markername"]
		if "Head Office" in location_name:
			continue

		raw_address = store["properties"]['address'].replace(", Canada","").replace("&amp;","&").replace("St Airdrie","St, Airdrie").replace("n Alberta","n, Alberta").strip().split(",")
		
		if len(raw_address) == 3:
			street_address = raw_address[0].strip()
			city = raw_address[1].replace("No. 44","").strip()
			state = raw_address[2].strip()[:3].strip()
			zip_code = raw_address[2].strip()[3:].strip()

			if zip_code == "T5Y":
				zip_code = "T5Y 2M4"
			if zip_code == "T1P":
				zip_code = "T1P 1M6"
			if zip_code == "T2B":
				zip_code = "T2B 2Y4"
			if street_address == "101 Sunset Dr":
				zip_code = "T4C 0W7"
			if len(zip_code) < 4:
				zip_code = "<MISSING>"
		elif len(raw_address) == 2:
			state = raw_address[-1].strip()
			if "Blvd" in raw_address[0]:
				street_address = raw_address[0].strip()
				city = "<MISSING>"
			else:
				street_address = " ".join(raw_address[0].split()[:-1])
				city = raw_address[0].split()[-1].strip()
			zip_code = "<MISSING>"

		country_code = "CA"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = "<MISSING>"
		hours_of_operation = "<MISSING>"
		latitude = store['geometry']['coordinates'][1]
		longitude = store['geometry']['coordinates'][0]
		link = "<MISSING>"

		# Store data
		data.append([locator_domain, "<MISSING>", location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
