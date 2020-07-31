from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json

from sgselenium import SgSelenium


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
	
	base_link = "https://www.paisanospizza.com/locations"

	driver.get(base_link)
	time.sleep(randint(6,8))

	data = []

	base = BeautifulSoup(driver.page_source,"lxml") 
	items = base.find_all(class_="yext-schema-json")
	locator_domain = "paisanospizza.com"

	for item in items:
		store = json.loads(item.text)

		location_name = store['name'] + " " + store['address']['addressLocality']
		print(location_name)

		street_address = store['address']['streetAddress']
		city = store['address']['addressLocality']
		state = store['address']['addressRegion']
		zip_code = store['address']['postalCode']

		country_code = "US"
		store_number = store['@id']
		
		location_type = "<MISSING>"
		phone = store['telephone']

		hours_of_operation = ""
		raw_hours = store['openingHoursSpecification']
		for hours in raw_hours:
			day = hours['dayOfWeek']
			opens = hours['opens']
			closes = hours['closes']
			clean_hours = day + " " + opens + "-" + closes
			hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
