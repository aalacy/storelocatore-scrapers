from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
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
	
	base_link = "https://www.wirelessm.net/locations"

	driver.get(base_link)
	time.sleep(randint(2,3))
	element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
		(By.ID, "masterPage")))
	time.sleep(randint(2,4))

	driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
	time.sleep(1)
	base = BeautifulSoup(driver.page_source,"lxml")

	data = []

	locator_domain = "wirelessm.net"
	items = base.find_all(class_="card")

	for item in items:
		location_name = item.h5.text.strip()
		print(location_name)
		raw_address = item.find(class_="col-12").text.replace(", Dallas 75252",", Dallas, TX 75252").replace(". Dallas TX",", Dallas, TX")\
		.replace("Mansfield TX","Mansfield, TX").replace(". Sunrise",", Sunrise,").replace(". Tamarac",", Tamarac")\
		.replace("Lauderdale","Lauderdale,").replace("Worth TX","Worth, TX").replace("Lewisville","Lewisville,").split(",")
		street_address = " ".join(raw_address[:-2]).strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()
		city = raw_address[-2].strip()
		state = raw_address[-1].strip()[:-6].strip()
		zip_code = raw_address[-1][-6:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = item.find(class_="col-10 m-0 p-0").text.strip()
		if "am " in phone:
			phone = "<MISSING>"
		hours_of_operation = item.find_all(class_="col-10 m-0 p-0")[-1].text.replace("• ","").strip()
		latitude = "<MISSING>"
		longitude = "<MISSING>"
		
		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
