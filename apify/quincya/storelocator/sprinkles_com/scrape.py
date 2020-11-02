from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sprinkles_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://sprinkles.com/sprinkles-cupcakes-bakery-ice-cream-and-atm-locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
		logger.info("Got today page")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.find_all(class_="location-teaser column large-4 small-12")
	
	data = []
	for item in items:
		locator_domain = "sprinkles.com"

		location_name = item.find("h4").text.strip()
		logger.info(location_name)

		street_address = item.find(class_="address-line1").text.strip()
		try:
			street_address = street_address + " " + item.find(class_="address-line2").text.strip()
			street_address = street_address.strip()
		except:
			pass

		if "New Locations Coming" in street_address:
			street_address = "<MISSING>"

		city = item.find(class_="locality").text.strip()
		state = item.find(class_="administrative-area").text.strip()
		zip_code = item.find(class_="postal-code").text.strip()
		country_code = "US"
		store_number = "<MISSING>"
		
		location_type = "<MISSING>"

		try:
			phone = item.find_all('a')[-1].text.strip()
			if "ATM" in phone:
				phone = "<MISSING>"
		except:
			phone = "<MISSING>"

		latitude = item.find(class_="location-teaser-geofield")["data-lat"]
		longitude = item.find(class_="location-teaser-geofield")["data-lng"]

		page_link = "https://sprinkles.com" + item.find('a')['href']
		page_req = session.get(page_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			page = BeautifulSoup(page_req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		hours_of_operation = ""
		raw_hours = page.find(class_="field-wrapper field field-with-icon field-node--field-hours field-name-field-hours field-type-text-long field-label-hidden")
		raw_hours = raw_hours.find_all("p")

		hours = ""
		hours_of_operation = ""

		try:
			for hour in raw_hours:
				if "Below are our" not in hour.text.strip():
					hours = hours + " " + hour.text.strip()
			hours_of_operation = (re.sub(' +', ' ', hours)).strip()
		except:
			pass
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()