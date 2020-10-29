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

	log.info("Filtering " + str(len(stores)) + " potential POIs..Could take a couple hours..")
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

		location_type = store['PosDescription'].split("-")[0]

		try:
			if "eye" in location_type.lower():
				link = "https://www.myeyelab.com/locations/" + store["webPath"]
			else:
				link = "https://www.stantonoptical.com/locations/" + store["webPath"]
		except:
			continue

		phone = store['phoneNumbers']["spd"]

		try:
			mon = "Monday " + store["MondayStart"].split(".")[0] + "-" + store["MondayEnd"].split(".")[0]
		except:
			mon = "Monday Closed"

		try:
			tue = " Tuesday " + store["TuesdayStart"].split(".")[0] + "-" + store["TuesdayEnd"].split(".")[0]
		except:
			tue = " Tuesday Closed"

		try:
			wed = " Wednesday " + store["WednesdayStart"].split(".")[0] + "-" + store["WednesdayEnd"].split(".")[0]
		except:
			wed = " Wednesday Closed"

		try:
			thu = " Thursday " + store["ThursdayStart"].split(".")[0] + "-" + store["ThursdayEnd"].split(".")[0]
		except:
			thu = " Thursday Closed"

		try:
			fri = " Friday " + store["FridayStart"].split(".")[0] + "-" + store["FridayEnd"].split(".")[0]
		except:
			fru = " Friday Closed"

		try:
			sat = " Saturday " + store["SaturdayStart"].split(".")[0] + "-" + store["SaturdayEnd"].split(".")[0]
		except:
			sat = " Saturday Closed"

		try:
			sun = " Sunday " + store["SundayStart"].split(".")[0] + "-" + store["SundayEnd"].split(".")[0]
		except:
			sun = " Sunday Closed"

		hours_of_operation = mon + tue + wed + thu + fri + sat + sun

		# try:
		# log.info(link)
		
		phone = "<INACCESSIBLE>"
		wait = 5

		for i in range(5):

			driver.get(link)

			element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
				(By.TAG_NAME, "body")))
			time.sleep(wait)
			if len(driver.page_source) > 200 and "bbB3q6Lt5ZQnwlTH1tZY0" in driver.page_source:
				base = BeautifulSoup(driver.page_source,"lxml")

				script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
				phone = json.loads(script)['telephone']

				if "Temporarily Closed" in base.text:
					hours_of_operation = "Temporarily Closed"

				break
			else:
				# log.info("Retrying ..")
				wait = wait + 5

		# Store data
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
