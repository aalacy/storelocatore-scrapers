from bs4 import BeautifulSoup
import csv
import time
from random import randint

import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('manchuwok_com')



def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://manchuwok.com/store-locator/"

	driver = get_driver()
	time.sleep(2)

	driver.get(base_link)
	time.sleep(10)
	
	base = BeautifulSoup(driver.page_source,"lxml")
	items = base.find_all(class_="results_wrapper")	

	data = []
	found_zips = []
	location_names = []

	locator_domain = "manchuwok.com"

	# Getting all names first
	for i in range(len(items)):
		item = items[i]
		location_name = "Manchuwok " + item.find(class_="results_row_right_column").span.text.strip()

		street_address = item.find(class_="slp_result_address slp_result_street").text.strip()
		try:
			street_address = street_address + " " + item.find(class_="slp_result_address slp_result_street2").text.strip()
			street_address = street_address.strip()
		except:
			pass

		location_names.append([location_name, street_address])

	for location in location_names:

		got_loc = False
		run_count = 0

		while not got_loc and run_count < 3:
			search_element = driver.find_element_by_id('addressInput')
			search_element.clear()
			time.sleep(randint(1,2))
			search_element.send_keys(location[0] + " " + location[1])
			time.sleep(randint(1,2))

			# Setting to 5 miles
			select = Select(driver.find_element_by_id('radiusSelect'))
			select.select_by_visible_text('5 miles')
			time.sleep(randint(1,2))

			search_button = driver.find_element_by_id('addressSubmit')
			driver.execute_script('arguments[0].click();', search_button)
			time.sleep(randint(10,12))

			sel_items = driver.find_elements_by_class_name("results_wrapper")
		
			base = BeautifulSoup(driver.page_source,"lxml")
			items = base.find_all(class_="results_wrapper")

			location_name = location[0]
			for i in range(0,len(items)):

				item = items[i]
				
				if location_name == "Manchuwok " + item.find(class_="results_row_right_column").span.text.strip():
					logger.info(location_name)
					got_loc = True

					street_address = item.find(class_="slp_result_address slp_result_street").text.strip()
					try:
						street_address = street_address + " " + item.find(class_="slp_result_address slp_result_street2").text.strip()
						street_address = street_address.strip()
					except:
						pass

					city_line = item.find(class_="slp_result_address slp_result_citystatezip").text.strip()
					city_line = re.sub(' +', ' ', city_line)
					city = city_line[:city_line.find(',')].strip()
					state = city_line[city_line.find(',')+1:city_line.find(',')+4].strip()
					if state == "PQ":
						state = "QC"
					zip_code = city_line[city_line.find(',')+4:city_line.rfind(',')].strip()
					if "canada" in city_line.lower():
						country_code = "CA"
					else:
						country_code = "US"

					store_number = "<MISSING>"
					location_type = "<MISSING>"

					try:
						phone = item.find(class_="slp_result_address slp_result_phone").text.strip()
						if not phone:
							phone = "<MISSING>"
					except:
						phone = "<MISSING>"
					
					hours_of_operation = item.find(class_="slp_result_contact slp_result_hours").text.replace("\n"," ").strip()
					if not hours_of_operation:
						hours_of_operation = "<MISSING>"

					sel_items[i].click()
					time.sleep(randint(3,4))
					try:
						raw_gps = driver.find_element_by_xpath("//*[(@title='Open this area in Google Maps (opens a new window)')]").get_attribute("href")
						latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
						longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()

						lat_long = latitude + "_" + longitude
						if lat_long in found_zips:
							latitude = "<MISSING>"
							longitude = "<MISSING>"
						else:
							found_zips.append(lat_long)
					except:
						latitude = "<MISSING>"
						longitude = "<MISSING>"

					data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
					break
			if not got_loc:
				logger.info("Missed: " + location_name + "..  Retrying ..")
				run_count = run_count + 1
	return data

	try:
		driver.close()
	except:
		pass

def scrape():
	data = fetch_data()
	write_output(data)

scrape()