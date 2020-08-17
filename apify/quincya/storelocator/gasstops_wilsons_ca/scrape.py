from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_links = ["https://gasstops.wilsons.ca/wp-admin/admin-ajax.php?action=store_search&lat=46.5653163&lng=-66.46191639999999&max_results=100&search_radius=500&filter=24",
				  "https://gasstops.wilsons.ca/wp-admin/admin-ajax.php?action=store_search&lat=53.1355091&lng=-57.6604364&max_results=100&search_radius=500&filter=24"]

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	found_poi = []
	for base_link in base_links:
		req = session.get(base_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		stores = json.loads(base.text)
		for store in stores:
			location_name = store["store"].replace("&#8217;","'").replace("–","-").replace("’","'")
			if location_name in found_poi:
				continue
			else:
				found_poi.append(location_name)
			locator_domain = "gasstops.wilsons.ca"
			street_address = store["address"]
			city = store["city"]
			state = store["state"]
			zip_code = "<MISSING>"
			country_code = "CA"
			store_number = store["id"]
			location_type = store["24HourLocation"]
			if location_type == "Yes":
				location_type = "24Hour Location"
			else:
				location_type = "Not 24Hour Location"
			phone = store["phone"]
			hours_of_operation = store["hours"]
			if not hours_of_operation:
				hours_of_operation = "<MISSING>"
			latitude = store["lat"]
			longitude = store["lng"]

			data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
