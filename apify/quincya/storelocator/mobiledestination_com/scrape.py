from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mobiledestination_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://mobiledestination.com/locations/"

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

	items = base.find_all(class_="elementor-price-list-item")
	locator_domain = "mobiledestination.com"

	for item in items:

		raw_data = item.p.text.strip().split("\n\n")

		location_name = item.find(class_="elementor-price-list-title").text.strip()
		logger.info(location_name)
		
		raw_address = item.p.text[:item.p.text.find("(")].strip().split(",")
		try:
			city = raw_address[-2].strip()
		except IndexError:
			raw_address = raw_data[2].split(",")
			city = raw_address[-2].strip()

		street_address = " ".join(raw_address[:-2]).strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()

		state = raw_address[-1].split()[0].strip()
		try:
			zip_code = raw_address[-1].split()[1].strip()
		except:
			zip_code = "<MISSING>"

		if street_address == "700 Davey Crockett Dr.":
			street_address = "700 Davey Crockett Dr. Suite 100"
			city = "New Boston"
			state = "TX"
			zip_code = "75570"
		if city == "4300 N Midland Drive":
			street_address = "4300 N Midland Drive Suite 101"
			city = "Midland"
			state = "TX"
			zip_code = "79707"

		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = item.p.text[item.p.text.find("("):item.p.text.rfind("Mon")].strip()
		hours_of_operation = item.p.text[item.p.text.rfind("Mon"):].replace("\n","").replace("\xa0","").replace("\u200b","").strip()
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
