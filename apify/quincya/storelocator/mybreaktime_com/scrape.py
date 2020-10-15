from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
import re

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = 'https://www.mybreaktime.com/wp-admin/admin-ajax.php?action=store_search&lat=37.96425&lng=-91.83183&max_results=100&search_radius=1000&filter=17&autoload=1'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	locator_domain = "mybreaktime.com"

	stores = json.loads(base.text.strip())

	for store in stores:
		location_name = store["store"]
		street_address = store["address"]
		if street_address != store["address2"]:
			street_address = (street_address + " " + store["address2"]).replace("Malone2823 E Malone Ave","Malone Ave").strip()
		city = store['city']
		state = store["state"]
		zip_code = store["zip"]
		country_code = "US"
		store_number = store["id"]
		location_type = "<MISSING>"
		phone = store['phone']
		hours_of_operation = store["hours"]
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"
		latitude = store['lat']
		longitude = store['lng']
		link = "<MISSING>"

		# Store data
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
