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
from selenium.webdriver.support.ui import Select


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

	base_link = "https://petvalu.com/store-locator/?location=ON,&radius=100"

	driver.get(base_link)
	time.sleep(randint(2,3))

	try:
		element = WebDriverWait(driver, 100).until(EC.presence_of_element_located(
			(By.ID, "store_locator_filter_radius")))
		time.sleep(randint(1,2))
	except:
		print("Timeout waiting on results..skipping")

	#CA
	ca_list = ["AB", "BC", "SK", "NS", "MB", "QC", "ON", "NT", "PE", "NL", "NU", "YT"]

	all_links = set()
	for ca_state in ca_list:
		print("Searching " + ca_state)
		search_element = driver.find_element_by_id("store_locator_province")
		search_element.clear()
		time.sleep(randint(1,2))
		try:
			search_element.send_keys(ca_state)
			time.sleep(randint(1,2))
		except:
			continue
		select_radius = Select(driver.find_element_by_id('store_locator_filter_radius'))
		select_radius.select_by_visible_text('100 km')
		time.sleep(randint(1,2))

		search_button = driver.find_element_by_id('store_locator_find_stores_button')
		driver.execute_script('arguments[0].click();', search_button)
		time.sleep(randint(4,6))
		try:
			element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
				(By.ID, "store_locator_result_list")))
			time.sleep(randint(1,2))
		except:
			try:
				search_element.clear()
				time.sleep(randint(1,2))
				search_element.send_keys(ca_state)
				time.sleep(randint(1,2))
				search_button = driver.find_element_by_id('store_locator_find_stores_button')
				driver.execute_script('arguments[0].click();', search_button)
				time.sleep(randint(4,6))
				element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
					(By.ID, "store_locator_result_list")))
				time.sleep(randint(1,2))
			except:
				print("Error..skipping")
				continue

		base = BeautifulSoup(driver.page_source,"lxml")
		raw_data = base.find(id="store_locator_result_list")
		items = raw_data.find_all(class_="store-locator-row")
		print("Found %s items" %(len(items)))
		for item in items:
			all_links.add(item.a['href'])

	#US
	base_link = "https://us.petvalu.com/store-locator/?location=PA,&radius=100"

	driver.get(base_link)
	time.sleep(randint(2,3))

	try:
		element = WebDriverWait(driver, 100).until(EC.presence_of_element_located(
			(By.ID, "store_locator_filter_radius")))
		time.sleep(randint(1,2))
	except:
		print("Timeout waiting on results..skipping")


	us_list = ['AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 
				'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MH', 'MA', 'MI', 'FM', 'MN', 'MS', 'MO', 'MT', 'NE', 
				'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PW', 'PA', 'PR', 'RI', 'SC', 
				'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'VI', 'WA', 'WV', 'WI', 'WY']

	for us_state in us_list:
		print("Searching " + us_state)
		search_element = driver.find_element_by_id("store_locator_province")
		search_element.clear()
		time.sleep(randint(1,2))
		try:
			search_element.send_keys(us_state)
			time.sleep(randint(1,2))
		except:
			continue
		select_radius = Select(driver.find_element_by_id('store_locator_filter_radius'))
		select_radius.select_by_visible_text('100 mi')
		time.sleep(randint(1,2))

		search_button = driver.find_element_by_id('store_locator_find_stores_button')
		driver.execute_script('arguments[0].click();', search_button)
		time.sleep(randint(4,6))
		try:
			element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
				(By.ID, "store_locator_result_list")))
			time.sleep(randint(1,2))
		except:
			try:
				search_element.clear()
				time.sleep(randint(1,2))
				search_element.send_keys(ca_state)
				time.sleep(randint(1,2))
				search_button = driver.find_element_by_id('store_locator_find_stores_button')
				driver.execute_script('arguments[0].click();', search_button)
				time.sleep(randint(4,6))
				element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
					(By.ID, "store_locator_result_list")))
				time.sleep(randint(1,2))
			except:
				print("Error..skipping")
				continue

		base = BeautifulSoup(driver.page_source,"lxml")
		raw_data = base.find(id="store_locator_result_list")
		items = raw_data.find_all(class_="store-locator-row")
		print("Found %s items" %(len(items)))
		for item in items:
			all_links.add(item.a['href'])

	data = []
	final_links = list(all_links)
	final_links.sort()
	for i, final_link in enumerate(final_links):
		print("Link %s of %s" %(i+1,len(final_links)))
		driver.get(final_link)
		time.sleep(randint(2,4))

		try:
			element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
				(By.CLASS_NAME, "address_info")))
			time.sleep(randint(1,2))
		except:
			print("Timeout..retrying..")
			driver.refresh()
			time.sleep(randint(2,4))
			try:
				element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
					(By.CLASS_NAME, "address_info")))
				time.sleep(randint(1,2))
			except:
				print("Timeout again..skipping")
				continue

		base = BeautifulSoup(driver.page_source,"lxml")
		
		location_name = base.find(class_="location_name").text.strip()
		
		if "us.pet" in final_link:
			locator_domain = "us.petvalu.com"
			country_code = "US"
		else:
			locator_domain = "petvalu.com"
			country_code = "CA"

		raw_address = str(base.find(class_='address_info'))
		raw_address = raw_address[raw_address.find(">")+1:].strip().split("<br/>")

		street_address = raw_address[0].strip()
		if "," in raw_address[2]:
			city_line = raw_address[2].strip().split(",")
			street_address = (street_address + " " + raw_address[1].strip()).strip()
		else:
			city_line = raw_address[1].strip().split(",")
		
		street_address = street_address.replace("&amp;","&")
		city = city_line[0].strip()
		state = city_line[1][:4].strip()
		zip_code = city_line[1][4:].strip()
		if country_code == "US" and len(zip_code) == 4:
			zip_code = "0" + zip_code
		if zip_code == "10531" and city == "Mahopac":
			zip_code = "10541"
		if zip_code == "L7H4O6" and location_name == "Burlington Walkers":
			zip_code = "L7M 4C6"
		store_number = final_link.split("/")[-2]
		if not store_number.isnumeric():
			store_number = "<MISSING>"
		location_type = ""
		try:
			raw_types = base.find(class_="services").find_all('p') 
			for loc_type in raw_types:
				location_type = (location_type + ", " + loc_type.text.strip()).strip()
			location_type = location_type[1:].strip()
			if not location_type:
				location_type = "<MISSING>"
		except:	
			location_type = "<MISSING>"

		try:
			phone = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', base.find(class_='address_info').text)[0].strip()
		except:
			try:
				phone = base.find_all(id="phone-desktop")[-1].text.strip()
			except:
				phone = "<MISSING>"
		if not phone:
			phone = "<MISSING>"

		# Maps
		try:
			raw_gps = base.find('iframe')['src']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
			longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		try:
			hours_of_operation = base.find(class_="hours").text.replace("HOURS","").replace("PM","PM ").strip()
		except:
			hours_of_operation = "<MISSING>"

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
