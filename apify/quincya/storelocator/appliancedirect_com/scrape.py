from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('appliancedirect_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.appliancedirect.com/contact"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	data = []

	items = base.find_all(class_="location")
	locator_domain = "appliancedirect.com"

	for item in items:

		raw_data = item.text.split("\n")

		location_name = item.h4.text.strip()
		# logger.info(location_name)
		
		raw_address = item.span.text.strip().split(",")
		while True:
			if "FL " not in raw_address[-1]:
				raw_address.pop(-1)
			else:
				break

		street_address = " ".join(raw_address[:-2]).strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()
		city = raw_address[-2].strip()
		state = raw_address[-1].strip()[:3].strip()
		zip_code = raw_address[-1][3:9].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		try:
			phone = item.a.text.replace("Phone:","").strip()
		except:
			phone = "<MISSING>"

		hours_of_operation = item.find_all("span")[-1].text.replace("Store Hours:","").replace("–","-").strip()

		try:
			map_link = item.find_all("a")[-1]['href']
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
