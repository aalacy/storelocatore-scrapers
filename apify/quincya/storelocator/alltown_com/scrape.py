from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('alltown_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://api.zenlocator.com/v1/apps/app_tx4vzjry/init?widget=MAP"

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

	data = []
	stores = json.loads(base.text)["locations"]

	locator_domain = "alltown.com"

	for store in stores:
		location_name = store['name']
		raw_address = store['address'].split(",")
		street_address = store['address1']
		if not street_address:
			street_address = raw_address[0].strip()
		city = store['city']
		if not city:
			city = raw_address[1].strip()
		state = store['region']
		zip_code = store['postcode']
		if not zip_code:
			zip_code = raw_address[-2].split()[-1]
		if zip_code == "06405":
			zip_code = "03032"
		country_code = store['countryCode']
		if country_code != "US":
			continue
		store_number = "<MISSING>"
		location_type = store["customText"]
		if not location_type:
			location_type = "<MISSING>"
		phone = store['contacts']['con_z6hc3bcn']['text']
		hours_of_operation = ""
		raw_hours = store['hours']['hoursOfOperation']
		for day in raw_hours:
			hours = day + " " +raw_hours[day]
			hours_of_operation = (hours_of_operation + " " + hours).strip()

		if location_type == "<MISSING>":
			if len(re.findall(r'12:00-12:00', hours_of_operation)) == 7:
				location_type = "24 Hours"
		latitude = store['lat']
		longitude = store['lng']

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
