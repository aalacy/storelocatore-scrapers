from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
import json
from sglogging import sglog

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://lemontree.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all(class_="book-check")
	locator_domain = "lemontree.com"
	log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)

	for item in items:
		link = item.a["href"]

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		fin_script = ""
		all_scripts = base.find_all('script')
		for script in all_scripts:
			if "latitude" in str(script):
				fin_script = script.text.replace('\n', '').strip()
				break
		
		js = base.text.split("var locations =")[1].split("];")[0] + "]"
		store = json.loads(js)[0]
		status = store["status_name"]

		if "coming" in status.lower():
			continue

		location_name = store["name"]
		log.info(link)
		location_name = "Lemon Tree Hair Salon - " + store["name"]
		street_address = ((store["fran_address"] + " " + store["fran_address_2"]).strip()).replace("<br>","")
		city = store['fran_city']
		state = store["fran_state_abbrev"]
		zip_code = store["fran_zip"]
		country_code = "US"
		store_number = store["id"]
		location_type = "<MISSING>"
		phone = store['fran_phone']
		hours_of_operation = base.find(class_="mb-2 small").text.replace("\r\n", " ").replace("Our salon is now open with limited hours by appointment.","").strip()
		hours_of_operation = hours_of_operation.replace("We will be closed Tuesday 8/26 - Sat 8/30 to allow our staff some time with family","")\
		.replace("All appointments must be booked online or by phone during our limited business hours. No walk-ins or salon waiting permitted at this time. Please arrive promptly at appointed times.","")\
		.replace("Appointments preferred. Please book online or by phone. Walk-ins welcome upon availability.","")\
		.replace("Walk-ins served on availability. We kindly ask that you honor your appointment time. 24-hour cancellation notice appreciated.","").strip()
		latitude = store['fran_latitude']
		longitude = store['fran_longitude']

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
