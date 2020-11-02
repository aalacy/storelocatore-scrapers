from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jacksonhealth_org')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://jacksonhealth.org/locations/?locationsFiltersName=&view=map"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all(class_="locations-carousel-item")
	locator_domain = "jacksonhealth.org"

	for item in items:
		link = item.a["href"]

		location_name = item.h3.text.replace("–","-").strip()
		logger.info(link)
		
		raw_address = item.p.text.split(",")
		street_address = " ".join(raw_address[:-3]).strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()
		city = raw_address[-3].strip()
		state = raw_address[-2].strip()
		zip_code = raw_address[-1].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		try:
			phone = item.find_all("a")[-2].text.replace("(Adult Outpatient Services)","").strip()
		except:
			phone = "<MISSING>"

		try:
			hours_of_operation = item.find_all("p")[1].text.replace("–","-").replace("North Dade Health Center is open","").strip()
		except:
			hours_of_operation = "<MISSING>"

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		latitude = base.find(class_="simple-map__map location-hero-map-wrapper__map-div")["data-lat"]
		longitude = base.find(class_="simple-map__map location-hero-map-wrapper__map-div")["data-lng"]

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
