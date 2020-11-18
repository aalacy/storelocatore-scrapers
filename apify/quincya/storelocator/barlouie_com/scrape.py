from sgrequests import SgRequests
import csv
import sgzip
from sgzip import SearchableCountries

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
			
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	found_poi = []

	locator_domain = "https://www.barlouie.com"

	coords = sgzip.coords_for_radius(radius=40, country_code=SearchableCountries.USA)
	for coord in coords:
		lat, lng = coord
		
		base_link = "https://www.barlouie.com/locations/search?latitude=%s&longitude=%s&index=0" %(lat,lng)
		stores = session.get(base_link, headers = HEADERS).json()

		for store in stores:
			
			link = locator_domain + store['u']
			if link in found_poi:
				continue
			found_poi.append(link)

			location_name = store['n']
			street_address = store['a']
			city = store['l']
			state = store['r']
			zip_code = store['pc']
			country_code = store['c']
			store_number = store['sn']
			location_type = "<MISSING>"
			phone = store['p']
			latitude = store['la']
			longitude = store['lo']
			raw_hours = store['h']
			hours_of_operation = ""
			for raw_hour in raw_hours:
				hours_of_operation = (hours_of_operation + " " + raw_hour['Value'] + " " + raw_hour['Key']).strip()

			if not hours_of_operation:
				hours_of_operation = "<MISSING>"
				
			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
