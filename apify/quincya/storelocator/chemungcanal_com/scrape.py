from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
from random import randint
import time
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('chemungcanal_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.chemungcanal.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	session = SgRequests()

	req = session.get(base_link, headers=headers)
	time.sleep(randint(2,4))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.find_all(class_="location-box height-100")
	logger.info("Got " + str(len(items)) + " locations")
	time.sleep(randint(1,2))

	data = []
	for item in items:
		locator_domain = "chemungcanal.com"
		location_name = item.h3.text.strip()
		logger.info(location_name)

		raw_address = item.find(class_="location-address").text.strip().split("\n")
		street_address = raw_address[0]
		city_line = raw_address[1]
		city = city_line[:city_line.find(',')].strip()
		state = city_line[city_line.find(',')+1:city_line.find(',')+4].strip()
		zip_code = city_line[-6:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = item.p.text.replace("Phone:","").strip()
		if "Toll" in phone:
			phone = phone[:phone.find("Toll")]
		location_type = "BRANCH"
		try:
			hours_of_operation = item.find(class_="location-hours").p.text.replace("Lobby & Drive-up:","").replace("\n"," ").strip()
		except:
			hours_of_operation = "<MISSING>"
		if "ATM" in location_name:
			phone = "<MISSING>"
			location_type = "ATM"
			hours_of_operation = "24hrs"
		elif "Main Office" in location_name:
			location_type = "MAIN OFFICE"

		# Maps
		# logger.info("Getting map info ..")
		map_link = item.find("a")['href']

		req = session.get(map_link, headers = headers)
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

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
