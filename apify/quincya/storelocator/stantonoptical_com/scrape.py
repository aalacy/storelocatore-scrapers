from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import json
import re

from sgselenium import SgSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="stantonoptical.com")


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

	base_link = 'https://www.stantonoptical.com/schedule-exam/'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	locator_domain = "stantonoptical.com"

	script = base.find('script', attrs={'type': "application/json"}).text.replace('\n', '').strip()
	stores = json.loads(script)["props"]['stores']

	log.info("Filtering " + str(len(stores)) + " potential POIs..Could take an hour..")
	for store in stores:
		location_name = store["WebDescription"].strip()
		street_address = (store["AddressLine1"] + " " + store["AddressLine2"] + " " + store["AddressLine3"]).strip()
		city = store['City']
		state = store["State"]
		zip_code = store["PostalCode"]
		country_code = store['Country']
		store_number = store["StoreNumber"]

		try:
			latitude = store['Latitude']
			longitude = store['Longitude']
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		if not latitude:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		location_type = store['PosDescription']

		try:
			if "eye" in location_type.lower():
				link = "https://www.myeyelab.com/locations/" + store["webPath"]
			else:
				link = "https://www.stantonoptical.com/locations/" + store["webPath"]
		except:
			continue
		
		driver.get(link)
		try:
			element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
				(By.CLASS_NAME, "bbB3q6Lt5ZQnwlTH1tZY0")))
			time.sleep(2)
		except:
			continue
		base = BeautifulSoup(driver.page_source,"lxml")

		phone = base.find(class_="bbB3q6Lt5ZQnwlTH1tZY0").text
		hr = json.loads(base.find('script', {'class': re.compile(r'.+-schema')}).text)

		hours_of_operation = ""
		raw_hours = hr['openingHoursSpecification']
		for hours in raw_hours:
			day = hours['dayOfWeek']
			if len(day[0]) != 1:
				day = ' '.join(hours['dayOfWeek'])
			opens = hours['opens']
			closes = hours['closes']
			if opens != "" and closes != "":
				clean_hours = (day + " " + opens + "-" + closes).replace("Closed-Closed","Closed")
				hours_of_operation = (hours_of_operation + " " + clean_hours).strip()
				hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()

		if "Temporarily Closed" in base.text:
			hours_of_operation = "Temporarily Closed"

		# Store data
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
