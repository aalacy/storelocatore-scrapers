from bs4 import BeautifulSoup
import csv
import time
import re

from selenium.webdriver.common.by import By	
from selenium.webdriver.support.ui import WebDriverWait	
from selenium.webdriver.support import expected_conditions as EC	
from selenium.common.exceptions import TimeoutException	
from selenium.webdriver.common.keys import Keys

from random import randint

from sgselenium import SgSelenium

driver = SgSelenium().chrome()

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.kenworth.com/dealers/"

	time.sleep(2)

	driver.get(base_link)
	time.sleep(randint(2,4))

	element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
		(By.ID, "findSearchBox")))
	time.sleep(randint(3,5))

	states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
		"HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
		"MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
		"NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
		"SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
		"Alberta","British Columbia","Manitoba","New Brunswick",
		"Newfoundland and Labrador","Northwest Territories","Nova Scotia",
		"Nunavut","Ontario","Prince Edward Island","Quebec","Saskatchewan","Yukon"]

	all_links = []
	found_links = []

	for state in states:
		print("State: " + state)
		search_element = driver.find_element_by_id("findSearchBox")
		search_element.send_keys(Keys.CONTROL + "a")
		search_element.send_keys(Keys.DELETE)
		search_element.send_keys(state)
		time.sleep(randint(1,2))
		search_button = driver.find_element_by_id('searchLocBtn')
		search_button.click()
		time.sleep(randint(6,8))

		try:
			element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
				(By.ID, "findResults")))
			time.sleep(randint(3,5))
		except:
			print("Timeout..no results found")

		try:
		  results = driver.find_element_by_id("findLocations").find_elements_by_tag_name("li")
		except:
			continue

		for result in results:
			item = result.find_element_by_css_selector(".button.ctaSub")
			link = item.get_attribute("href")

			if link not in found_links:
				latitude = result.find_element_by_id("findDirections").find_element_by_tag_name("a").get_attribute("endlat")
				longitude = result.find_element_by_id("findDirections").find_element_by_tag_name("a").get_attribute("endlng")
				found_links.append(link)
				all_links.append([link, latitude, longitude])

	data = []
	total_links = len(all_links)
	for i, raw_link in enumerate(all_links):
		print("Link %s of %s" %(i+1,total_links))
		link = raw_link[0]
		latitude = raw_link[1]
		longitude = raw_link[2]
		
		driver.get(link)
		time.sleep(randint(1,2))

		element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
			(By.TAG_NAME, "h1")))

		element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
			(By.CLASS_NAME, "phone-listing")))
		time.sleep(randint(2,4))

		item = BeautifulSoup(driver.page_source,"lxml")

		locator_domain = "kenworth.com"
		location_name = item.find('h1').text.strip()

		if not location_name:
			time.sleep(randint(5,8))

		item = BeautifulSoup(driver.page_source,"lxml")
		location_name = item.find('h1').text.strip()
		print(location_name)

		raw_address = item.find(class_="address").text.strip()

		street_address = raw_address[:raw_address.rfind(",")].strip()
		zip_code = raw_address[-6:].strip()
		if " " in zip_code:
			country_code = "CA"
			zip_code = raw_address[-7:].strip()
			if zip_code == "S9H 5RH":
				zip_code = "S0N 2Y0"
				state = "SK"
				city = "Swift Current"
			else:
				state = raw_address[raw_address.find(zip_code)-3:raw_address.find(zip_code)].strip()
				city = raw_address[raw_address.rfind(",")+1:raw_address.find(zip_code)-3].strip()
		else:
			country_code = "US"
			if "-" in zip_code:
				zip_code = raw_address[raw_address.rfind(" ")+1:].strip()		
			state = raw_address[raw_address.find(zip_code)-3:raw_address.find(zip_code)].strip()
			city = raw_address[raw_address.rfind(",")+1:raw_address.find(zip_code)-3].strip()
		if state == "NF":
			state = "NL"

		store_number = link.split("=")[-1]
		try:
			phone = item.find(class_="phone-main").text.replace("Phone: ","").strip()
		except:
			phone = "<MISSING>"

		location_type = item.find(class_="dealership-type").text.strip()
		if not location_type:
		  location_type = "<MISSING>"

		try:
			raw_hours = item.find(class_="operation-hours").find_all("tr")[1:]
			hours = []

			for raw_hour in raw_hours:
				day = raw_hour.find("th").text.strip()
				hour = raw_hour.find("td").text.strip()
				hours.append([day, hour])

			hours_of_operation = [y for x in hours for y in x]
			hours_of_operation = " ".join(hours_of_operation)
		except:
			pass
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	
	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
