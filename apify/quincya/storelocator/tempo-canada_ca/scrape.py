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
	
	base_link = 'https://www.digitalservices.crs/coopcrsapi/locations?storeBrand=TMPO'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	stores = session.get(base_link, headers = HEADERS).json()['locations']

	data = []
	locator_domain = "tempo-canada.ca"

	for store in stores:
		location_name = store["name"].encode("ascii", "replace").decode().replace("?","e")
		street_address = store["streetAddress"].strip()
		city = store['city']
		state = store["province"]
		zip_code = store["postalCode"]
		country_code = "CA"
		store_number = store["locationID"]
		location_type = ""
		try:
			services = store['services']
			try:
				for loc_type in services:
					location_type = (location_type + "," + loc_type['serviceType']).strip()
				location_type = location_type[1:].strip()
			except:
				location_type = services['serviceType']
		except:
			location_type = "<MISSING>"
		phone = store['phone']
		hours_of_operation = ""
		raw_hours = ""
		services = ""
		try:
			raw_hours = store['services']['hours']
			try:
				hours_of_operation = (hours_of_operation + " " + raw_hours['day'] + " " + raw_hours['open'] + "-" + raw_hours['open']).strip()
			except:
				for raw_hour in raw_hours:
					hours_of_operation = (hours_of_operation + " " + raw_hour['day'] + " " + raw_hour['open'] + "-" + raw_hour['open']).strip()
		except:
			try:
				services = store['services']
				for service in services:
					try:
						raw_hours = service['hours']
						break
					except:
						continue
				try:
					hours_of_operation = (hours_of_operation + " " + raw_hours['day'] + " " + raw_hours['open'] + "-" + raw_hours['open']).strip()
				except:
					for raw_hour in raw_hours:
						hours_of_operation = (hours_of_operation + " " + raw_hour['day'] + " " + raw_hour['open'] + "-" + raw_hour['open']).strip()
			except:
				hours_of_operation = "<MISSING>"
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"
		latitude = store['latitude']
		longitude = store['longitude']
		link = store["website"]
		if not link:
			link = "<MISSING>"

		# Store data
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
