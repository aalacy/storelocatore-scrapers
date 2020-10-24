from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://cremedelacreme.com/wp-admin/admin-ajax.php?action=store_search&lat=37.09024&lng=-95.71289&max_results=100&search_radius=500&autoload=1"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	stores = session.get(base_link, headers = HEADERS).json()

	data = []
	locator_domain = "cremedelacreme.com"

	for store in stores:
		location_name = store['store'].encode("ascii", "replace").decode().replace("?","e").split(",")[0].replace("IL","").split("&#")[0].strip()
		if "OPENING SOON" in location_name.upper():
			continue
		street_address = (store['address'] + " " + store['address2']).strip()
		city = store['city']
		state = store['state']
		zip_code = store['zip']
		country_code = "US"
		store_number = store['id']
		location_type = "<MISSING>"
		phone = store['phone']
		try:
			hours = BeautifulSoup(store['hours'],"lxml")
			hours_of_operation = " ".join(list(hours.stripped_strings))
		except:
			hours_of_operation = "<MISSING>"
		latitude = store['lat']
		longitude = store['lng']
		link = store['permalink']

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
