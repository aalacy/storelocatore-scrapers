from bs4 import BeautifulSoup
import csv
import time
from random import randint

from sgselenium import SgSelenium

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('friospops_com')




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

	base_link = "https://friospops.com/locations/"

	driver.get(base_link)
	time.sleep(randint(2,3))

	element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
		(By.CLASS_NAME, "elementor-inner")))
	time.sleep(randint(1,2))

	base = BeautifulSoup(driver.page_source,"lxml")
	items = base.find_all(class_="entry-title")

	final_links = []
	for item in items:
		final_links.append(item.a["href"])

	data = []
	for i, final_link in enumerate(final_links):
		logger.info("Link %s of %s" %(i+1,len(final_links)))
		logger.info(final_link)

		driver.get(final_link)
		time.sleep(randint(2,3))

		element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
			(By.CLASS_NAME, "elementor-inner")))
		time.sleep(randint(1,2))

		base = BeautifulSoup(driver.page_source,"lxml")

		locator_domain = "friospops.com"
		location_name = "Frios Gourmet Pops - " + base.find_all(class_="elementor-text-editor elementor-clearfix")[0].text
		# logger.info(location_name)
		
		try:
			raw_address = base.find_all(class_="elementor-text-editor elementor-clearfix")[1].p.text.split("\n")
		except:
			raw_address = base.find_all(class_="elementor-text-editor elementor-clearfix")[2].text
		
		if raw_address != "Historic Downtown McKinney":
			if "coming soon" in raw_address[0].lower():
				continue
			try:
				street_address = raw_address[-3].strip() + " " + raw_address[-2].strip()
			except:
				try:
					street_address = raw_address[-2].strip()
				except:
					continue

			city_line = raw_address[-1].split(",")
			city = city_line[0].strip()
			
			zip_code = city_line[-1][-6:].strip()
			if zip_code.isnumeric():
				state = city_line[1].split()[0].strip()
			else:
				try:
					state = city_line[1].strip()
					zip_code = "<MISSING>"
				except:
					street_address = raw_address[0].strip()
					city_line = raw_address[1].split(",")
					city = city_line[0].strip()
					state = city_line[1].split()[0].strip()
					zip_code = city_line[-1][-6:].strip()
		else:
			street_address = "Historic Downtown"
			city = "McKinney"
			state = "TX"
			zip_code = "<MISSING>"

		if "come to you" in street_address and "Charlotte, NC" in base.find_all(class_="elementor-text-editor elementor-clearfix")[1].p.text:
			street_address = "<MISSING>"
			city = "Charlotte"
			state = "NC"
			zip_code = "<MISSING>"
		if "fun van" in street_address.lower():
			street_address = "<MISSING>"

		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = base.find_all(class_="elementor-text-editor elementor-clearfix")[3].text.strip()
		if not phone:
			phone = "<MISSING>"
		hours_of_operation = base.find_all(class_="elementor-text-editor elementor-clearfix")[5].text.replace("\n"," ").strip()
		if not hours_of_operation or "events" in hours_of_operation:
			hours_of_operation = "<MISSING>"

		hours_of_operation = hours_of_operation.replace("–","-")
		
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
