from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('theathletesfoot_com')



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

	locator_domain = "theathletesfoot.com"

	data = []
	found_poi = []

	for coord_search in sgzip.coords_for_radius(200):
		lat = coord_search[0]
		lng = coord_search[1]
		base_link = "https://theathletesfoot.com/wp-admin/admin-ajax.php?action=store_search&lat=%s&lng=%s&max_results=100&search_radius=500" %(lat,lng)
		logger.info(base_link)

		req = session.get(base_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		stores = json.loads(base.text)		

		for store in stores:
			link = store['permalink']
			if link in found_poi:
				continue
			found_poi.append(link)
			location_name = store['store']
			street_address = store['address2']
			if not street_address:
				street_address = store['address']
			city = store['city']
			state = store['state']
			zip_code = store['zip']
			if not zip_code:
				zip_code = "<MISSING>"
			country_code = store['country']
			if "US" in country_code:
				country_code = "US"
			else:
				continue
			store_number = link.split("-")[-1].replace("/","")
			location_type = "<MISSING>"
			phone = store['phone']
			if not phone:
				phone = "<MISSING>"
			hours_of_operation = store['hours']
			if not hours_of_operation:
				hours_of_operation = "<MISSING>"
			latitude = store['lat']
			longitude = store['lng']
			
			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
