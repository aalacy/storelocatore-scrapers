from bs4 import BeautifulSoup
import csv
import re
import time
from random import randint

from sgselenium import SgSelenium

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="lecreuset.com")

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.lecreuset.com/stores"

	driver = SgSelenium().chrome()
	time.sleep(2)

	driver.get(base_link)
	all_links =  []

	element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
		(By.CLASS_NAME, "card-body")))
	time.sleep(randint(3,5))

	base = BeautifulSoup(driver.page_source,"lxml")
	items = base.find_all(class_="store-item col-12 col-md-3")
	for item in items:
		all_links.append(item.find(class_="btn btn-link")["href"])

	data = []
	log.info("Getting " + str(len(all_links)) + " links. Can take up to an hour.")
	for link in all_links:
		# log.info(link)
		driver.get(link)

		element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
			(By.CLASS_NAME, "storelocator-detals")))
		time.sleep(randint(1,2))

		base = BeautifulSoup(driver.page_source,"lxml")

		locator_domain = "lecreuset.com"
		location_name = base.h1.text.strip()
		location_type = "<MISSING>"

		raw_data = list(base.find(class_="col-12 col-md-6 store-information").div.stripped_strings)

		street_address = raw_data[0].strip()
		if "Caymans Islands" in street_address:
			continue
		city_line = raw_data[1].replace("\n"," ").strip()
		if city_line == "null":
			raw_data_line = raw_data[0].replace("Blvd.,","Blvd.")
			city = " ".join(raw_data_line.split(",")[:-1]).split()[-1].strip()
			street_address = raw_data_line[:raw_data_line.rfind(city)].strip()
			state = raw_data_line.split(",")[-1].split()[0].strip()
			zip_code = raw_data_line.split(",")[-1].split()[1].strip()
		elif len(city_line) > 4:
			city = city_line.split(",")[0].strip()
			state = city_line.split(",")[1].split()[0].strip()
			zip_code = city_line.split(",")[1].split()[1].strip()
		else:
			raw_data_line = raw_data[0].replace("Blvd.,","Blvd.")
			street_address = " ".join(raw_data_line.split(",")[0].split()[:-1])
			city = raw_data_line.split(",")[0].split()[-1]
			state = raw_data_line.split(",")[1].split()[0].strip()
			zip_code = raw_data_line.split(",")[1].split()[1].strip()

		if len(zip_code) == 4:
			zip_code = "0" + zip_code
		if "null" in zip_code:
			zip_code = "<MISSING>"

		if "Suite" in city:
			street_address = street_address + " " + " ".join(city.split()[:2])
			city = " ".join(city.split()[2:])
		if "Suite 125 Miramar" in street_address:
			street_address = street_address.replace("Miramar","").strip()
			city = "Miramar Beach"
		if "1911 Leesburg-Grove City" in street_address:
			street_address = street_address.replace("1098 Grove","1098").strip()
			city = "Grove City"
		if "Canal St New" in street_address:
			street_address = street_address.replace("Canal St New","Canal St").strip()
			city = "New York"
			
		country_code = "US"
		store_number = "<MISSING>"
		phone = raw_data[-1].strip()
		zip_code = zip_code.replace("01007","10013")
		
		try:
			hours_of_operation = base.find(class_='store-hours').text.replace("Hours","").replace("\n"," ").split("Email")[0].strip()
		except:
			hours_of_operation = "<MISSING>"

		map_link = base.find(class_="store-map")["href"]
		latitude = map_link.split("=")[-1].split(",")[0]
		longitude = map_link.split("=")[-1].split(",")[1]

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
