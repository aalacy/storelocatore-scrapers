from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cote_co_uk')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.cote.co.uk/wp-content/uploads/locations.js"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	locator_domain = "cote.co.uk"

	stores = json.loads(base.text.replace("var locationList =","").strip())

	for store in stores:
		link = store["link"]
		logger.info(link)

		location_name = store['post_title']
		street_address = (store['address_1'] + " " + store['address_2']).replace("`","'").strip()
		if street_address[-1:] == ",":
			street_address = street_address[:-1]
		city = store['town_city']
		state = "<MISSING>"
		zip_code = store['postcode']
		country_code = "GB"
		store_number = store['ID']
		phone = store['phone_number']
		latitude = store['location']['lat']
		longitude = store['location']['lng']

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_type = base.find_all(class_="w-6/12 px-1 font-serif text-18 leading-16")[-1].text.replace("Facilities","").strip().replace("\n\n","").replace("\n",",").replace("•","").replace(" , ","").strip()
		location_type = (re.sub(' +', ' ', location_type)).strip()
		hours_of_operation = base.find_all(class_="w-6/12 px-1 font-serif text-18 leading-16")[-2].text.replace("Opening Times","").strip().replace("\n\n","").replace("\n"," ").strip()
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
		
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
