from bs4 import BeautifulSoup
import csv
import time
import re
import sgzip

from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


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
	
	main_link = "https://www.golfgalaxy.com/s/stores"
	base_link = "https://storelocator.golfgalaxy.com/index_single.html"

	driver = get_driver()
	time.sleep(2)

	driver.get(base_link)
	time.sleep(randint(8,10))

	# # Clear ad
	# try:
	# 	ad_close = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "close")))
	# 	driver.execute_script('arguments[0].click();', ad_close)
	# except:
	# 	pass

	# element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dsg_stores")))
	# frame_link = driver.find_element_by_id("dsg_stores").get_attribute("src")
	# driver.get(frame_link)

	element = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, "search_address")))

	data = []
	poi_done = []
	zips = sgzip.for_radius(200)
	total_zips = str(len(zips))
	count = 1
	for zip_code in zips[:3]:
		print("Searching: " + str(zip_code))
		print("# " + str(count) + " of " + total_zips)
		print()
		count = count + 1

		search_element = driver.find_element_by_id("search_address")
		search_element.clear()
		time.sleep(randint(1,2))
		search_element.send_keys(zip_code)
		time.sleep(randint(1,2))
		search_button = driver.find_element_by_id('search_button')
		driver.execute_script('arguments[0].click();', search_button)
		time.sleep(randint(8,10))

		base = BeautifulSoup(driver.page_source,"lxml")

		results = base.find_all(class_='location_row')[1:]

		for result in results:
			locator_domain = "golfgalaxy.com"
			location_name = result.find(class_='store_name').text.strip()

			shop_center = result.find(class_='shopping_center').text.strip()
			address1 = result.find(class_='address1').text.strip()
			street_address = (shop_center + " " + address1).strip()
			

			test_string = location_name + "_" + street_address
			if test_string in poi_done:
				continue

			poi_done.append(test_string)

			print(location_name)
			city_line = result.find(class_='city_state_postalcode').text.strip()
			city = city_line[:city_line.find(',')].strip()
			state = city_line[city_line.find(',')+1:city_line.rfind(' ')].strip()
			zip_code = city_line[city_line.rfind(' ')+1:].strip()
			country_code = "US"

			store_number = "<MISSING>"
			try:
				phone = result.find(class_='phone').text.strip()
			except:
				phone = "<MISSING>"

			location_type = "<MISSING>"

			raw_hours = result.find(class_="all_hours_table").find_all('tr')
			hours = ""
			hours_of_operation = ""

			try:
				for hour in raw_hours:
					hours = hours + " " + hour.text.replace("\t","").replace("\n"," ").strip()
				hours_of_operation = (re.sub(' +', ' ', hours)).strip()
			except:
				pass
			if not hours_of_operation:
				hours_of_operation = "<MISSING>"

			latitude = "<MISSING>"
			longitude = "<MISSING>"

			data.append([locator_domain, main_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	
	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
