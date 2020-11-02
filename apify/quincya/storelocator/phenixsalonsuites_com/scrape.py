from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('phenixsalonsuites_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://phenixsalonsuites.com/locations-list/"

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

	items = base.find_all(class_="location_details_page_link")
	locator_domain = "phenixsalonsuites.com"

	for i, item in enumerate(items):
		logger.info(str(i+1) + " of " + str(len(items)))
		final_link = item.a['href']

		req = session.get(final_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
			logger.info(final_link)
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		location_name = base.h2.text.strip()
		# logger.info(location_name)

		street_address = base.find(class_="location_adress").text.strip()
		city_line = base.find(class_="location_tot").text.strip().split("\xa0")
		city = city_line[0].replace(",","").strip()
		state = city_line[1].strip()
		zip_code = city_line[-1].strip()
		if zip_code == "07473" and location_name == "North Haven":
			zip_code = "06473"
		if zip_code == "28210" and location_name == "Parkville (Parkway Crossing)":
			zip_code = "21234"


		country_code = "US"
		store_number = final_link.split("=")[-1]
		
		location_type = "<MISSING>"

		try:
			phone = base.find(class_="location_phone").text.replace("Phone:","").replace("?","").replace("Leasing","").strip()
			if "flopez" in phone or "Rental" in phone or "Text" in phone:
				phone = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}',phone)[0]
			if not phone[-3:].strip().isnumeric():
				phone = "<MISSING>"
		except:
			phone = "<MISSING>"

		hours_of_operation = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
