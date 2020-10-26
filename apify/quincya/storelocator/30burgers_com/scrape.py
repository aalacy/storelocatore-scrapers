from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('30burgers_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.30burgers.com/food-and-restaurants-locations"

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

	items = base.find(class_="location_info").find_all("li")
	locator_domain = "30burgers.com"

	for item in items:

		raw_data = item.text.split("\n")

		location_name = raw_data[0].strip()
		logger.info(location_name)
		
		raw_address = raw_data[1].split(",")
		try:
			city = raw_address[-2].strip()
		except IndexError:
			raw_address = raw_data[2].split(",")
			city = raw_address[-2].strip()

		street_address = " ".join(raw_address[:-2]).strip()
		
		state = raw_address[-1].strip()[:-6].strip()
		zip_code = raw_address[-1][-6:].strip()

		country_code = "US"
		store_number = "<MISSING>"
		
		location_type = "<MISSING>"

		try:
			phone =  re.findall("[[(\d)]{3}-[\d]{3}-[\d]{4}", str(item))[0]
		except:
			phone = "<MISSING>"

		hours_of_operation = "<MISSING>"

		try:
			map_link = item.a['href']
			at_pos = map_link.rfind("!3d")
			latitude = map_link[at_pos+3:map_link.rfind("!")].strip()
			longitude = map_link[map_link.find("!4d", at_pos)+3:].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
