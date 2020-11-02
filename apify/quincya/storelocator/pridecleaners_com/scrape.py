from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pridecleaners_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://pridecleaners.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all(class_="gv-grid gv-map-view-main-attr")
	locator_domain = "pridecleaners.com"

	for item in items:

		location_name = item.h3.text.strip()
		# logger.info(location_name)
		
		raw_address = list(item.p.stripped_strings)

		street_address = raw_address[0].replace("Kansas City, MO","").replace("Liberty, MO","").strip()
		city_line = raw_address[1].strip().split(",")
		city = city_line[0].strip()
		state = city_line[1].strip().split()[0].strip()
		try:
			zip_code = city_line[1].strip().split()[1].strip()
		except:
			zip_code = "<MISSING>"

		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		try:
			phone = item.find(class_="gv-field-1-4").text
		except:
			phone = "<MISSING>"

		hours_of_operation = "<MISSING>"
		
		map_link = item.find(class_="map-it-link")['href']
		try:
			req = session.get(map_link, headers = HEADERS)
			maps = BeautifulSoup(req.text,"lxml")
			raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
			longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
		except:
			latitude = '<MISSING>'
			longitude = '<MISSING>'

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
