from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('odeon_co_uk')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.odeon.co.uk/cinemas/london/"

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

	items = base.find_all(class_="btn blue")[1:]
	locator_domain = "odeon.co.uk"

	for item in items:

		link = "https://www.odeon.co.uk" + item["href"]
		logger.info(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		
		raw_address = json.loads(base.find(id="cinemasData")['data-cinemasmap'])[0]

		location_name = raw_address['name']
		street_address = raw_address['address']['lineOne']
		city = raw_address['address']['lineTwo']
		state = "<MISSING>"
		zip_code = raw_address['address']['postcode']
		country_code = "GB"
		store_number = raw_address['siteId']
		if raw_address['isImax'] == 1:
			location_type = "IMAX"
		else:
			location_type = "Cinema"
		phone = "<MISSING>"
		hours_of_operation = "<MISSING>"
		latitude = raw_address['latitude']
		longitude = raw_address['longitude']

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
