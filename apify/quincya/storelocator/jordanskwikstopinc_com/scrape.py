from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jordanskwikstopinc_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	driver = SgSelenium().chrome()
	time.sleep(2)
	
	base_link = "https://jordanskwikstopinc.com/locations/"

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

	items = base.find_all('div', attrs={'style': "font-size:1.6em"})
	locator_domain = "jordanskwikstopinc.com"

	for item in items:

		raw_data = str(item.p).replace("<p>","").replace("</p>","").replace(" AR ", ",AR ").replace(",,", ",").split("<br/>")
		location_name = item.a.text.strip()
		logger.info(location_name)

		street_address = raw_data[0].replace(",","").strip()
		city = raw_data[1].split(',')[0].strip()
		state = raw_data[1].split(',')[1].strip().split()[0]
		zip_code = raw_data[1].split(',')[1].strip().split()[1]
		country_code = "US"
		store_number = location_name.split("#")[-1]
		location_type = "<MISSING>"
		phone = "<MISSING>"
		hours_of_operation = "<MISSING>"

		map_link = item.a['href']
		if "page" in map_link or "maps" in map_link:
			driver.get(map_link)
			time.sleep(randint(8,10))
			try:
				map_link = driver.current_url
				at_pos = map_link.rfind("@")
				latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
				longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()

				if not latitude[3:5].isnumeric():
					latitude = "<MISSING>"
					longitude = "<MISSING>"
			except:
				latitude = "<INACCESSIBLE>"
				longitude = "<INACCESSIBLE>"
		else:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
