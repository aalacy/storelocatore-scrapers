from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
import json

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.orangeshoe.com/PersonalTrainingStudios"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all(class_="studioInfo")
	locator_domain = "orangeshoe.com"

	for item in items:

		link = "https://www.orangeshoe.com" + item.a["href"]
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
		store = json.loads(script)

		location_name = store['name']
		city = store['address']['addressLocality']
		raw_address = base.find(class_="locFooterAddress").text
		street_address = raw_address[:raw_address.find(city)].strip()
		state = store['address']['addressRegion']
		zip_code = store['address']['postalCode']
		country_code = "US"

		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = store['telephone']

		hours_of_operation = ""
		raw_hours = store['openingHoursSpecification']
		for hours in raw_hours:
			day = hours['dayOfWeek']
			if len(day[0]) != 1:
				day = ' '.join(hours['dayOfWeek'])
			opens = hours['opens']
			if opens != "":
				clean_hours = day + " " + opens
				hours_of_operation = (hours_of_operation + " " + clean_hours).strip()
		hours_of_operation = hours_of_operation.replace("NONE","Closed")
		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
