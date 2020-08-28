from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
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

	base_link = "https://smiledirectclub.com/api/locations/stores/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	locator_domain = "smiledirectclub.com"

	stores = json.loads(base.text)

	for store in stores:

		country_code = store['country']
		if country_code not in ["US","CA"]:
			continue

		link = "https://smiledirectclub.com/smileshops/" + store["store_slug"]
		
		location_name = store['name']
		street_address = store['street1'] + " " + store['street2']
		street_address = (re.sub(' +', ' ', street_address)).replace("Inside","inside").strip()
		if "inside" in street_address:
			street_address = street_address[:street_address.find("inside")].strip()
		city = store['locality']
		state = store['region']
		zip_code = store['postal_code']
		store_number = store['id']
		location_type = store['location_type']
		if location_type == 6:
			location_type = "Inside CVS"
		elif location_type == 1:
			location_type = "Main Location"
		elif location_type == 2:
			location_type = "Pop Up"
		phone = store['phone']
		if not phone:
			phone = store['thanks_phone_number']
		hours_of_operation = ""
		raw_hours = store['hours_display']
		for raw_hour in raw_hours:
			hours_of_operation = hours_of_operation + " " + raw_hour[0] + " " + raw_hour[1] 
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
		latitude = store['latitude']
		longitude = store['longitude']
		
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
