from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('10gym_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://10gym.com/locations/"

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

	items = base.find_all(class_="col-md-4 col-sm-6 col-xs-12 col-xs-full lct_iterm")
	locator_domain = "10gym.com"

	for item in items:

		location_name = item.h2.text.strip()
		logger.info(location_name)
		
		raw_address = item.find(class_="lct_info").find_all("div")[-1].find_all("span")
		street_address = raw_address[0].text.strip()	
		city = raw_address[1].text.replace(",","").strip()
		state = raw_address[2].text.strip()
		zip_code = raw_address[3].text.strip()

		country_code = "US"
		store_number = item['id'].replace("lct_","")		
		location_type = "<MISSING>"

		try:
			phone =  re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", str(item))[0]
		except:
			phone = "<MISSING>"

		hours_of_operation = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
