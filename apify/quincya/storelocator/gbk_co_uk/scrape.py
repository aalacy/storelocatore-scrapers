from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('gbk_co_uk')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.gbk.co.uk/distance/get-locations/search"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	locator_domain = "gbk.co.uk"

	stores = json.loads(base.text)["locations"]

	for store in stores:
		link = "https://www.gbk.co.uk" + store["link"].split('"')[1]
		logger.info(link)

		location_name = store['title']
		raw_address = store['full_address'].split(",")
		street_address = " ".join(raw_address[:-2]).strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()
		city = city = raw_address[-2].strip()
		state = "<MISSING>"
		zip_code = raw_address[-1].strip()
		if zip_code == "The Moor S1 4PA":
			zip_code = "S1 4PA"
			street_address = "Unit 8, 24, The Moor"
			city = "Sheffield"
		country_code = "GB"
		store_number = store['id']
		location_type = "<MISSING>"
		latitude = store['lat']
		longitude = store['lng']

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		phone = base.find(class_="gbk gbk-phone").text.strip()
		hours_of_operation = base.find(class_="location-opening-times").text.replace("opening hours","").replace("Open","").strip().replace("\n"," ")
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
