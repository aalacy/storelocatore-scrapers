from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('loveandsandwiches_com')



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
	
	base_link = "http://loveandsandwiches.com/locations/"

	driver.get(base_link)
	time.sleep(randint(2,4))
	base = BeautifulSoup(driver.page_source,"lxml")

	data = []

	items = base.find_all(class_="LocationCon")
	locator_domain = "loveandsandwiches.com"

	for item in items:

		raw_data = item.text.split("\n")

		location_name = item.find(class_="storeFriendlyName").text
		logger.info(location_name)

		street_address = item.find(class_="storeAddress1").text
		city = item.find(class_="storeAddress2").text.split(",")[0].strip()
		state = item.find(class_="storeAddress2").text.split(",")[1].split()[0].strip()
		zip_code = item.find(class_="storeAddress2").text.split(",")[1].split()[1].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = item.find(class_="PhoneNumber").text.strip()
		if not phone:
			phone = "<MISSING>"
		hours_of_operation = item.find(class_="hours").text.strip()
		latitude = item["data-lat"]
		longitude = item["data-lon"]

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
