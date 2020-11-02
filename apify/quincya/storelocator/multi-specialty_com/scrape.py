from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('multi-specialty_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.multi-specialty.com/location-search/"

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

	items = base.find_all(class_="singlelocation-wrapper")
	locator_domain = "multi-specialty.com"

	for item in items:
		location_name = item.h3.text.strip()
		logger.info(location_name)
		start_num = 8

		street_address = item.find_all("p")[start_num-7].text.strip()
		try:
			street_address1 = item.find_all("p")[start_num-8].text.strip()
			if "hrs" not in street_address1.lower():
				street_address = (street_address1 + " " + street_address).strip()
		except:
			pass
		raw_address = item.find_all("p")[start_num-6].text.strip().split(",")
		city = raw_address[0].strip()
		state = raw_address[1].strip()
		zip_code = raw_address[2].strip()

		country_code = "US"
		store_number = item['class'][1].split("-")[1]
		location_type = "<MISSING>"
		phone = item.find_all("p")[start_num-5].text.strip()
		if "," in phone:
			phone = phone.split(",")[0]
		hours_of_operation = "<MISSING>"

		map_link = item.find_all("p")[-3].a['href']
		req = session.get(map_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			maps = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		try:
			raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
			longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		if street_address == "1305 W 7th St, Ste 15A":
			latitude = "39.431492"
			longitude = "-77.4201058"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
