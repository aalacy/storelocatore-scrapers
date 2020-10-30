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
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	driver = SgSelenium().chrome()
	
	base_link = "https://www.hy-vee.com/stores/gas-station-finder-results.aspx?zip=&state=&city=&diesel=False&e85=False&24hour=False&atm=False&fuelcall=False"

	driver.get(base_link)
	element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
		(By.CLASS_NAME, "paging")))
	time.sleep(randint(2,3))

	data = []

	last_page = driver.find_element_by_class_name("paging").find_elements_by_tag_name("a")[-2].text

	locator_domain = "hy-vee.com"

	for i in range(int(last_page)):

		base = BeautifulSoup(driver.page_source,"lxml")
		items = base.find(class_="icon_results").find_all("table")[:-1]		
		# geos = re.findall(r'maps.LatLng\([0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\)',str(base))

		for i in range(len(items)):
			item = items[i]
			# geo = geos[i]

			location_name = item.strong.text.strip()

			raw_address = list(item.stripped_strings)
			street_address = raw_address[1].strip()
			city = raw_address[2].split(",")[0].strip()
			state = raw_address[2].split(",")[1].strip()[:-6].strip()
			zip_code = raw_address[2].split(",")[1].strip()[-6:].strip().replace("51264","61264")

			phone = raw_address[-1].strip()
			country_code = "US"
			store_number = "<MISSING>"
			
			types = item.find("div").find_all("img")
			location_type = ""
			for raw_type in types:
				location_type = (location_type + ", " + raw_type["alt"])
			location_type = location_type[2:].strip().replace("\n","")
			location_type = (re.sub(' +', ' ', location_type)).strip()

			hours_of_operation = "<MISSING>"
			# latitude = geo.split("(")[1].split(",")[0]
			# longitude = geo.split("(")[1].split(",")[1].split(")")[0]
			latitude = "<MISSING>"
			longitude = "<MISSING>"

			data.append([locator_domain, "<MISSING>", location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

		curr_page = driver.find_element_by_class_name("current_page").text
		if curr_page == last_page:
			break

		next_page = driver.find_element_by_id("ctl00_cph_main_content_spuGasFinderResults_gvStores_ctl10_btnNext")
		driver.execute_script('arguments[0].click();', next_page)
		time.sleep(randint(5,7))
		
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
