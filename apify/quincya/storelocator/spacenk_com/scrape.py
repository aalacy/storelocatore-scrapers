from bs4 import BeautifulSoup
import csv
import time
from random import randint
from sgselenium import SgSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.spacenk.com/us/en_US/stores.html#!"

	driver = SgSelenium().chrome()
	time.sleep(2)

	driver.get(base_link)
	time.sleep(randint(1,2))

	actions = ActionChains(driver)

	try:
		element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
			(By.CSS_SELECTOR, ".ubsf_locations-list")))
		time.sleep(randint(1,2))
	except:
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	# Load full list
	total_poi = ""
	prev_total = 0
	count = 0
	while total_poi != prev_total and count < 10:
		element = driver.find_elements_by_class_name("ubsf_locations-list-item")[-1]
		actions.move_to_element(element).perform()
		time.sleep(4)
		prev_total = total_poi
		base = BeautifulSoup(driver.page_source,"lxml")
		total_poi = len(base.find_all(class_="ubsf_locations-list-item"))
		count += 1

	base = BeautifulSoup(driver.page_source,"lxml")

	data = []
	final_links = []

	final_items = base.find_all(class_="ubsf_locations-list-item")
	for final_item in final_items:
		name = final_item.find(class_="ubsf_locations-list-item-name").text
		if "Space NK Bloomingdale" in name:
			continue
		state = final_item.find(class_="ubsf_locations-list-item-zip-city").text
		state = state[state.rfind(",")+1:-6].strip()
		final_link = final_item.a['href']
		final_links.append([final_link,state])

	for final in final_links:
		final_link = final[0]

		driver.get(final_link)
		time.sleep(randint(1,2))

		try:
			element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
				(By.CSS_SELECTOR, ".ubsf_details-details-title")))
			time.sleep(randint(1,2))
		except:
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		item = BeautifulSoup(driver.page_source,"lxml")

		try:
			hours_of_operation = item.find(class_="ubsf_details-opening-hours").text.replace("pm","pm ").replace("closed","").strip()
		except:
			# Duplicates have no hours so skip
			continue
		
		print(final_link)
		locator_domain = "spacenk.com"
		location_name = item.h1.text
		# print(location_name)

		raw_address = item.find(class_="ubsf_details-address").text.split(",")
		street_address = raw_address[0].strip()
		city = raw_address[1].strip()
		state = final[1]
		zip_code = raw_address[2].strip()
		if len(zip_code) > 5:
			zip_code = zip_code[-5:]
		country_code = "US"
		store_number = final_link.split("/")[-1]
		location_type = "<MISSING>"
		phone = item.find(class_="ubsf_details-phone").text

		try:
			raw_gps = item.find(class_="ubsf_details-box-top-buttons-top").a['href']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
			longitude = raw_gps[raw_gps.find(",")+1:].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

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
