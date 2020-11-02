from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('burgerim_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://burgerim.com/?hcs=locatoraid&hca=search%3Asearch%2F%2Fproduct%2F_PRODUCT_%2Flat%2F%2Flng%2F%2Flimit%2F500"

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
	locator_domain = "burgerim.com"

	store_data = json.loads(base.text)["results"]
	for store in store_data:
		if "coming-soon" in store["mapicon"]:
			continue
		location_name = store['name']
		street_address = store['street1'].strip()
		city = store['city']
		state = store['state']
		zip_code = store['zip'].strip()
		if zip_code == "55608":
			zip_code = "95608"
		if zip_code == "32502":
			zip_code = "23502"
		country_code = "US"
		store_number = store['id']
		location_type = "<MISSING>"
		try:
			phone = store['phone']
			if not phone:
				phone = "<MISSING>"
		except:
			phone = "<MISSING>"
		if phone == "551-224-800":
			phone = "<MISSING>"
		hours_of_operation = (store["misc2"] + " " + store["misc1"]).strip()
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		latitude = store['latitude']
		longitude = store['longitude']
		if not latitude:
			latitude = "<MISSING>"
			longitude = "<MISSING>"


		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
