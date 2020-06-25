from bs4 import BeautifulSoup
import csv
import time
from random import randint

import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
	time.sleep(8)
	
	base = BeautifulSoup(driver.page_source,"lxml")
	items = base.find_all(class_="results_wrapper")

	data = []
	for item in items:
		locator_domain = "manchuwok.com"

		location_name = "Manchuwok " + item.find(class_="results_row_right_column").span.text.strip()
		print(location_name)

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

		try:
			gmaps_link = item.find(class_="storelocatorlink")['href']
			g_link = gmaps_link[:gmaps_link.find("?")+1] +  gmaps_link[gmaps_link.find("daddr"):]
			driver.get(g_link)
			time.sleep(randint(8,10))

			map_link = driver.current_url
			if "@" in map_link[map_link.rfind("/"):map_link.rfind("/")+3]:
				latitude = "<MISSING>"
				longitude = "<MISSING>"
			else:
				at_pos = map_link.rfind("@")
				latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
				longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()