from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
import sgzip

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

	base_link = "https://russellcellular.com/wp-admin/admin-ajax.php"
	locator_domain = "russellcellular.com"

	data = []
	found_poi = []

	search = sgzip.ClosestNSearch()
	# Initialize the search for the US only
	search.initialize(country_codes = ['us'])

	coords = search.next_coord()

	while coords:
		
		result_coords = []
		print(coords)

		lat = coords[0]
		lng = coords[1]

		# Request post
		payload = {'action':'localpages',
					'lat': lat,
					'lon': lng}

		response = session.post(base_link,headers=HEADERS,data=payload)
		base = BeautifulSoup(response.text,"lxml")

		items = base.find_all('div', attrs={'style': "display:none"})
		for item in items:
			location_name = item.strong.text.strip()
			if "soon" in location_name.lower():
				continue
			raw_address = str(item.find(class_="infobox")).split("<br/>")[1:-2]
			street_address = " ".join(raw_address[:-1]).strip()
			if "{" in street_address:
				street_address = street_address[:street_address.find("{")].strip()
			if street_address in found_poi:
				continue
			print(street_address)
			found_poi.append(street_address)
			city_line = raw_address[-1].strip().split(",")
			city = city_line[0].strip()
			state = city_line[-1].strip().split()[0].strip()
			zip_code = city_line[-1].strip().split()[1].strip()
			country_code = "US"
			store_number = "<MISSING>"
			location_type = "<MISSING>"
			phone = item.a.text.strip()
			hours_of_operation = "<MISSING>"
			try:
				geo = json.loads(item["data-gmapping"])
				latitude = geo["latlng"]["lat"]
				longitude = geo["latlng"]["lng"]
				result_coords.append((latitude, longitude))
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"
				
			data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

		print("max count update..")
		search.max_count_update(result_coords)
		coords = search.next_coord()

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
