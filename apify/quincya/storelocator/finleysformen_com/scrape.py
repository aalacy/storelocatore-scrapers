from bs4 import BeautifulSoup
import csv
import time
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
	
	base_link = "https://finleysbarbershop.com/locations/"

	driver = SgSelenium().chrome()
	time.sleep(2)

	data = []

	driver.get(base_link)
	time.sleep(2)

	element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
		(By.CLASS_NAME, "vc_tta-tab")))
	time.sleep(2)

	base = BeautifulSoup(driver.page_source,"lxml")

	panels = base.find(class_="vc_tta-panels").find_all(class_="vc_tta-panel") 
	locator_domain = "finleysbarbershop.com"

	for panel in panels:

		items = panel.find_all(class_="wpgmaps_mlist_row")
		link = base_link + "#" + panel["id"]
		for item in items:
			location_name = item.p.text.strip()
			
			raw_address = item["data-address"].replace("F620 Westlake","F620, Westlake").replace("Avenue, Suite","Avenue Suite").replace("Road, Suite","Road Suite").split(",")

			if len(raw_address) == 3:
				street_address = raw_address[0].strip()
				city = raw_address[1].strip()
			else:
				street_address = " ".join(raw_address[0].split()[:-1]).strip()
				city = raw_address[0].split()[-1].strip()

			state = raw_address[-1].strip()[:-6].upper().strip()
			zip_code = raw_address[-1][-6:].strip()

			country_code = "US"
			store_number = "<MISSING>"
			location_type = "<MISSING>"
			phone = item.h4.text.strip()
			hours_of_operation = item.find(class_="loc-txt-descr").p.text.replace("PM","PM ").replace("OPEN","").replace("\xa0"," ").strip()
			hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()

			latitude = item["data-latlng"].split(",")[0].strip()
			longitude = item["data-latlng"].split(",")[1].strip()

			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
