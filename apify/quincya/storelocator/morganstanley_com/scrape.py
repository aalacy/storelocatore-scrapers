from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
import json
from sgselenium import SgChrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="morganstanley.com")


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://advisor.morganstanley.com/search?profile=16348&profile=16350&q=Morgan%20Stanley&r=2500"

	driver = SgChrome().chrome()
	time.sleep(2)
	
	driver.get(base_link)
	element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
		(By.CLASS_NAME, "Teaser-title")))
	time.sleep(2)

	while True:

		print ("Scrolling to load full page ...")

		# Get scroll height
		last_height = driver.execute_script("return document.body.scrollHeight")

		# Scroll down to bottom
		try:
			next_page = driver.find_element_by_css_selector(".Results-seeMore.Button--hollow.js-locator-seeMore")
			driver.execute_script('arguments[0].click();', next_page)
		except:
			break

		# Wait to load page
		time.sleep(randint(3,5))

		# Calculate new scroll height and compare with last scroll height
		new_height = driver.execute_script("return document.body.scrollHeight")

		if new_height == last_height:

			# Try again to confirm 
			try:
				next_page = driver.find_element_by_css_selector(".Results-seeMore.Button--hollow.js-locator-seeMore")
				driver.execute_script('arguments[0].click();', next_page)
			except:
				break

			# Wait to load page
			time.sleep(randint(4,6))

			# Calculate new scroll height and compare with last scroll height
			new_height = driver.execute_script("return document.body.scrollHeight")

			# Check if the page height has remained the same
			if new_height == last_height:
				# if so, you are done
				print ("Done scrolling!")
				break
			# If not, move on to the next loop
			else:
				print ("Scroll again ...")
				last_height = new_height

	base = BeautifulSoup(driver.page_source,"lxml")
	items = base.find_all(class_="ResultList-item")

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	found_poi = []

	locator_domain = "morganstanley.com"

	log.info("Processing " + str(len(items)) + " links..")
	for item in items:

		location_name = item.span.text.strip()

		try:
			street_address = item.find(class_="c-address-street-1").text.strip() + " " + item.find(class_="c-address-street-2").text.strip()
		except:
			street_address = item.find(class_="c-address-street-1").text.strip()

		city = item.find(class_="c-address-city").text.strip()
		state = item.find(class_="c-address-state").text.strip()
		zip_code = item.find(class_="c-address-postal-code").text.strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = item.find(id="telephone").text.strip()
		hours_of_operation = "<MISSING>"

		try:
			link = item.find(class_="Teaser-titleLink Link Link--primaryPlain")["href"]
		except:
			link = "<MISSING>"
			if location_name in ["Morgan Stanley Pasadena Branch","Morgan Stanley Austin Branch", "Morgan Stanley Wichita Branch","Morgan Stanley Short Hills Branch"]:
				continue

		if location_name in found_poi:
			continue

		print(location_name)
		found_poi.append(location_name)
		try:
			map_link = item.find(class_="c-address").a["href"]
			req = session.get(map_link, headers = HEADERS)
			maps = BeautifulSoup(req.text,"lxml")

			try:
				raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
				latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
				longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
