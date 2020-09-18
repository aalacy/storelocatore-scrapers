from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
import sgzip
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

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}
	session = SgRequests()

	locator_domain = "champschicken.com"

	data = []
	found_poi = []

	for coord_search in sgzip.coords_for_radius(50):
		lat = coord_search[0]
		lng = coord_search[1]
		base_link = "https://mdsinternal.pfsbrands.com/store_locator/getstoresfull.php?lat=%s&lon=%s&brand=28" %(lat,lng)

		req = session.get(base_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		stores = json.loads(base.text)["stores"]
		locator_domain = "champschicken.com"

		for store in stores:
			link = "https://champschicken.com/locations/" + store['name'].lower() + '-' + store['city'].lower() + '-' + store['state'].lower() + ".html"
			link = link.replace(" ","-").replace("'","-").replace("-&-","-").replace("#","").replace(",","").replace("(","-").replace(")","-").replace(".-","-")
			link = (re.sub('-+', '-', link)).strip()
			if len(link.split("/")) == 6:
				link = "/".join(link.split("/")[:-1]) + "-" + link.split("/")[-1]
			if link in found_poi:
				continue
			print(link)
			found_poi.append(link)
			location_name = "Champs Chicken - " + store['name']
			try:
				street_address = (store['street_1'] + " " + store['street_2']).strip()
			except:
				street_address = store['street_1'].strip()
			if "Attn:" in street_address:
				street_address = street_address[:street_address.find("Attn:")].strip()
			city = store['city']
			state = store['state']
			zip_code = store['zip']
			if not zip_code:
				zip_code = "<MISSING>"
			country_code = "US"
			store_number = store['id']
			location_type = "<MISSING>"
			phone = store['phone']
			if not phone:
				phone = "<MISSING>"
			try:
				hours_of_operation = "Mon: " + store['monday_from'] + " " + store['monday_to'] + " " + "Tue: " + store['tuesday_from'] + " " + store['tuesday_to'] + " " + "Wed: " + store['wednesday_from'] + " " + store['wednesday_to']\
				 + " " + "Thu: " + store['thursday_from'] + " " + store['thursday_to'] + " " + "Fri: " + store['friday_from'] + " " + store['friday_to'] + " " + "Sat: " + store['saturday_from'] + " " + store['saturday_to']\
				 + " " + "Sun: " + store['sunday_from'] + " " + store['sunday_to']
				hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
				if hours_of_operation == "Mon: Tue: Wed: Thu: Fri: Sat: Sun:":
					hours_of_operation = "<MISSING>"
			except:
				hours_of_operation = "<MISSING>"
			latitude = store['lat']
			longitude = store['lon']
			
			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
