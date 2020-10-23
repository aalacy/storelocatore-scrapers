from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('navarro_com')



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

	base_link = "https://www.navarro.com/store-locator.htm"

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

	items = base.find(class_="store_addresses").find_all("li")
	locator_domain = "navarro.com"

	for item in items:

		location_name = item.span.text
		logger.info(location_name)

		raw_address = str(item.a).split("span>")[-1].replace("</a>","").split(",")
		if len(raw_address) < 4:
			street_address = raw_address[0].strip()
		else:
			street_address = "".join(raw_address[:2]).strip()
		city = raw_address[-2].strip()
		state = raw_address[-1].strip().split()[0]
		zip_code = raw_address[-1].strip().split()[1]

		country_code = "US"
		store_number = item.span.text.split("#")[-1]
		
		location_type = "<MISSING>"
		phone = str(item.p).split("<br/>")[0][-14:].strip()
		if phone[:1] == "0":
			phone = str(item.p).split("<br/>")[0][-16:].strip()
			phone = phone.replace(" - ","-")
		raw_hours = item.p.text
		hours = raw_hours[raw_hours.find("STORE")+6:raw_hours.find("PHAR")].replace("\n","").strip()
		hours_of_operation = (re.sub(' +', ' ', hours)).strip()

		map_link = item.a['href']
		driver.get(map_link)
		time.sleep(randint(6,8))
		try:
			map_link = driver.current_url
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
