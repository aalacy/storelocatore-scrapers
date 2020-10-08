from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
import json
from sgselenium import SgSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.tillys.com/stores/"

	driver = SgSelenium().chrome()
	time.sleep(2)

	driver.get(base_link)
	time.sleep(10)

	base = BeautifulSoup(driver.page_source,"lxml")

	data = []
	locator_domain = "tillys.com"

	script = base.find(id="primary").find_all(class_="spacing-top")[1].script.text.strip()
	stores = json.loads(script)

	for store in stores:
		location_name = store['name']
		if "Coming Soon" in location_name:
			continue
		# street_address = (store['address1'] + " " + store['address2']).strip()
		street_address = store['address1']
		city = store['city']
		state = store['stateCode']
		zip_code = store['postalCode']
		country_code = store['countryCode']
		store_number = store['id']
		if not store_number.isnumeric():
			store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = store['phone']
		hours_of_operation = "<INACCESSIBLE>"
		latitude = store['latitude']
		longitude = store['longitude']
		link = store['storeUrl']

		# Get hours from link (CURRENTLY GETTING BLOCKED BY WEBSITE)

		# driver.get(link)
		# element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
		# 	(By.CLASS_NAME, "sl__details_content")))
		# time.sleep(randint(4,8))

		# hours_of_operation = ""
		# days = list(base.find_all(class_="sl__details_content")[-1].div.stripped_strings)
		# hours = list(base.find_all(class_="sl__details_content")[-1].find_all("div")[1].stripped_strings)
		# for i in range(len(days)):
		# 	hours_of_operation = (hours_of_operation + days[i] + " " + hours[i] + " ")
		# hours_of_operation = hours_of_operation.strip()

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
