from sgrequests import SgRequests
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
	
	base_link = "https://www.wegmans.com/stores/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	data = []

	items = base.find(id="wegmans-maincontent").find_all("a", href=re.compile("/stores/")) 
	locator_domain = "wegmans.com"

	for i, item in enumerate(items):
		print("Link %s of %s" %(i+1,len(items)))
		link = "https://www.wegmans.com" + item['href']
		if "comhttps" in link:
			link = item['href']
		location_name = item.text.strip()

		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
			print(link)
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')
		
		store_js = base.find(class_="yoast-schema-graph").text
		store = json.loads(store_js)
		raw_data = store['@graph'][1]['description']
		if "Store Opening" in raw_data:
			continue
			
		raw_address = raw_data.split("•")[0].strip().split(",")
		city = raw_address[-2].strip()
		state = raw_address[-1].strip().split()[0].strip()
		if "New" in state:
			state = "NY"
		if "North" in state:
			state = "NC"
		zip_code = raw_address[-1].strip().split()[-1].replace(".","").strip()

		if "•" in raw_data:
			street_address = " ".join(raw_address[:-2]).strip()
			phone = raw_data.split("•")[1].strip()
			if len(phone) > 15:
				phone = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', raw_data)[0]
		else:
			try:
				street_address = raw_data[raw_data.rfind("at")+3:raw_data.rfind(city)].replace(",","").strip()
				phone = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', raw_data)[0]
			except:
				phone = "<MISSING>"

		country_code = "US"
		store_number = base.find(id="store-number").text
		
		types = base.find_all(class_="directions-subhead")
		location_type = ""
		for raw_type in types:
			location_type = (location_type + ", " + raw_type.text).strip()
		location_type = location_type[2:]

		hours_of_operation = base.find(class_="row map-content").find_all(class_="row")[2].text.strip()
		if "To comply" in hours_of_operation:
			hours_of_operation = hours_of_operation[:hours_of_operation.find("To comply")].strip()
		try:
			driver.get(link)
			element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
				(By.CLASS_NAME, "google-map-store-pin")))
			time.sleep(randint(1,2))
			raw_gps = driver.find_element_by_xpath("//*[(@title='Open this area in Google Maps (opens a new window)')]").get_attribute("href")
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
			longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
