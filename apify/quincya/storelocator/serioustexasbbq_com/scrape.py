from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('serioustexasbbq_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.serioustexasbbq.com/locations.php"

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

	items = base.find_all(class_="location-col")
	locator_domain = "serioustexasbbq.com"

	for item in items:

		raw_data = item.text.replace(", 8"," 8").strip().split("\r\n")

		location_name = "<MISSING>"

		street_address = raw_data[0].strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()
		# logger.info(street_address)
		city_line = raw_data[1].strip().split(",")
		city = city_line[0].strip()
		state = city_line[1][:-6].strip()
		zip_code = city_line[1][-6:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = raw_data[2].strip()

		hours_of_operation = ""
		raw_hours = raw_data[-2:]
		for hours in raw_hours:
			if "pm" in hours:
				hours_of_operation = (hours_of_operation + " " + hours.replace("Map and Directions","").strip()).strip()
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		try:
			map_link = item.a['href']
			req = session.get(map_link, headers = HEADERS)
			map_link = req.url
			latitude = map_link.split("~")[0].split("=")[-1]
			longitude = map_link.split("~")[1].split("&")[0]
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		if street_address == "2001 S Timberline Rd":
			latitude = "40.561459"
			longitude = "-105.039811"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
