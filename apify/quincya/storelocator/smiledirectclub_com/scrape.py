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
	
	base_link = "https://smiledirectclub.com/smileshops/?country-chooser-choice=US"

	driver.get(base_link)
	time.sleep(randint(2,4))
	try:
		element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
			(By.CLASS_NAME, "store-link")))
		time.sleep(randint(2,4))
	except:
		print("Failed to load home page..retrying..")

	driver.get(base_link)
	time.sleep(randint(2,4))
	try:
		element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
			(By.CLASS_NAME, "store-link")))
		time.sleep(randint(2,4))
	except:
		print("Failed to load home page..retrying..")

	base = BeautifulSoup(driver.page_source,"lxml")

	items = base.find_all(class_="store-link")
	locator_domain = "smiledirectclub.com"

	data = []

	for item in items:
		link = "https://smiledirectclub.com/" + item["href"].replace("../","")
		print(link)

		driver.get(link)
		time.sleep(randint(2,4))

		element = WebDriverWait(driver, 100).until(EC.presence_of_element_located(
			(By.CLASS_NAME, "details")))
		time.sleep(randint(2,4))
		
		base = BeautifulSoup(driver.page_source,"lxml")
		raw_data = base.find(class_="row content")

		try:
			location_name = raw_data.h3.text
		except:
			location_name = "<MISSING>"
		
		raw_address = raw_data.find(class_="details").find_all("p")

		street_address = raw_address[0].text.strip()
		city_line = raw_address[1].text.strip()
		city = city_line.split(",")[0].strip()
		state = city_line.split(",")[1].strip().split()[0]
		zip_code = city_line.split(",")[1].strip().split()[1]
		country_code = "US"
		store_number = "<MISSING>"
		if "pop-up" in link:
			location_type = "Pop Up"
		else:
			location_type = "Location"
		phone = raw_data.find(class_="bold teal not-thin").text
		hours_col1 = raw_data.find_all(class_="hours-display-col")[1].find_all("span")
		hours_col2 = raw_data.find_all(class_="hours-display-col")[2].find_all("span")
		hours_of_operation = ""
		for i, row in enumerate(hours_col1):
			line = hours_col1[i].text + " " + hours_col2[i].text
			hours_of_operation = (hours_of_operation + " " + line).strip()

		try:
			raw_gps = driver.find_element_by_xpath("//*[(@title='Open this area in Google Maps (opens a new window)')]").get_attribute("href")
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
			longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
