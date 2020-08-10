from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json

from sgselenium import SgSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
	
	base_link = "https://www.nandos.co.uk/restaurants/all"

	driver.get(base_link)
	time.sleep(randint(10,12))

	base = BeautifulSoup(driver.page_source,"lxml")

	data = []

	items = base.find_all(class_="accordion-listing__item")
	locator_domain = "nandos.co.uk"

	for i, item in enumerate(items):
		print("Link %s of %s" %(i+1,len(items)))
		link = "https://www.nandos.co.uk" + item.a['href']
		print(link)

		driver.get(link)
		time.sleep(randint(2,3))

		element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
			(By.CLASS_NAME, "pane__title")))
		time.sleep(randint(1,2))

		base = BeautifulSoup(driver.page_source,"lxml")

		script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
		store = json.loads(script)

		location_name = store['name']
		street_address = store['address']['streetAddress']
		city = store['address']['addressLocality']
		state = store['address']['addressRegion']
		if not state:
			state = "<MISSING>"
		zip_code = store['address']['postalCode']
		if not zip_code:
			zip_code = "<MISSING>"
		country_code = "GB"

		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = store['contactPoint'][0]['telephone']
		if phone == "+44":
			phone = "<MISSING>"
		hours_of_operation = store['openingHours'][0]
		if hours_of_operation == "mo-su -":
			hours_of_operation = "<MISSING>"

		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']
		if not latitude:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		if "Blanchardstown Rd S" in street_address:
			latitude = "53.3917382"
			longitude = "-6.3979187"
			
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
