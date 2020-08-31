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
	
	base_link = "http://www.champlainfarms.com/wp-json/champlain/v1/stores/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")
	data = []

	stores = json.loads(base.text)["features"]
	locator_domain = "champlainfarms.com"

	for store in stores:
		street_address = store['properties']['address'].replace("St.","St,").split(",")[0]
		city = store['properties']['city']
		if not city and street_address == "188 First St":
			city = "Swanton"
		elif not city:
			city = "<MISSING>"
		state = store['properties']['state']
		zip_code = store['properties']['postalCode']
		country_code = "US"

		store_number = store['properties']['store_num']
		phone = store['properties']['phone']
		if not phone:
			phone = "<MISSING>"

		latitude = store['geometry']['coordinates'][1]
		longitude = store['geometry']['coordinates'][0]

		link = store['properties']['permalink']
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.h3.text.strip()
		location_type = base.find(class_="location-data").ul.text.strip().replace("\n",",")
		try:		
			hours_of_operation = base.find(id="store_timings").text.strip().replace("\n",",")
		except:
			hours_of_operation = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
