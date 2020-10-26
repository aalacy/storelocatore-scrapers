from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('svsports_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.svsports.com/storelocator.cfm"

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

	items = base.find_all(class_="mapAddress")
	locator_domain = "svsports.com"

	for item in items:

		raw_data = item.text.split("\n")
		raw_address = raw_data[1].split(",")
		city = raw_address[0].strip()
		state = raw_address[1].strip()

		street_address = raw_data[3].strip()

		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = raw_data[4].strip()
		if "Suite" in phone:
			street_address = street_address + " " + " ".join(phone.split()[:2])
			phone = phone.split()[-1]			
		raw_gps = item.h4['onclick']
		latitude = re.findall(",[0-9]{2,3}\.[0-9].+,", raw_gps)[-1].replace(",","")
		longitude = re.findall("-[0-9]{2,3}\.[0-9].+\)", raw_gps)[-1].replace(")","")

		link = item.find_all("a")[-1]['href']
		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
			logger.info(link)
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
		store_data = json.loads(script)

		location_name = base.find(class_="page-heading").text.strip()
		zip_code = store_data['address']['postalCode']

		hours_of_operation = ""
		raw_hours = store_data['openingHoursSpecification']
		for hours in raw_hours:
			day = hours['dayOfWeek']
			if len(day[0]) != 1:
				day = ' '.join(hours['dayOfWeek'])
			opens = hours['opens']
			closes = hours['closes']
			clean_hours = day + " " + opens + "-" + closes
			hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
