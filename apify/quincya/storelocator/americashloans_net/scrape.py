from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('americashloans_net')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://americashloans.net/locations/locations-by-state/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all(class_="list-group-item")
	locator_domain = "americashloans.net"

	for item in items:
		link = "https://americashloans.net" + item.a["href"]
		logger.info(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.h1.text.strip()

		raw_address = base.find(class_="location-meta-info-sub").text.strip().split("\r\n")
		if len(raw_address) == 1:
			raw_address = base.find(class_="location-meta-info-sub").text.strip().split("\n")
		street_address = raw_address[0].strip()
		city = raw_address[1].split(",")[0].strip()
		state = raw_address[1].split(",")[1].split()[0].strip()
		zip_code = raw_address[1].split(",")[1].split()[1].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		try:
			phone = base.find(class_="button-seperator").find_all("a")[-1]["href"].replace("tel:","").strip()
		except:
			phone = "<MISSING>"

		raw_hours = str(base.find(class_="location-meta-info"))[3:]
		hours_of_operation = raw_hours[raw_hours.find(">")+1:raw_hours.find("<")].replace("\r\n"," ").replace("\n"," ").strip()
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()

		map_data = base.find(id="map")
		latitude = map_data["data-latitude"]
		longitude = map_data["data-longitude"]

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
