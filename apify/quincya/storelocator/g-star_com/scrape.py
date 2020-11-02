from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('g-star_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.g-star.com/en_us/find-a-store/getstores?country_iso=US&output_details=1"

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
	locator_domain = "g-star.com"

	store_data = json.loads(base.text)["results"]
	for store in store_data:
		location_name = store['name1']
		street_address = store['address']['streetname']
		city = store['address']['city']
		state = store['address']['state']
		zip_code = store['address']['postalCode']
		country_code = "US"
		store_number = store['storeId']
		location_type = "<MISSING>"
		phone = store['telephoneNumber']
		mon = "Mon " + store["monday"]
		tue = " Tue " + store["tuesday"]
		wed = " Wed " + store["wednesday"]
		thu = " Thu " + store["thursday"]
		fri = " Fri " + store["friday"]
		sat = " Sat " + store["saturday"]
		sun = " Sun " + store["sunday"]
		hours_of_operation = mon+tue+wed+thu+fri+sat+sun

		latitude = store['latitude']
		longitude = store['longitude']
		link = "https://www.g-star.com" + store['contentPageUrl']
		if link != "https://www.g-star.com":
			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
