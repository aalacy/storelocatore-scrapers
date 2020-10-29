from sgselenium import SgSelenium
from bs4 import BeautifulSoup
import csv
import time
import re
from random import randint
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('abcstores_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://abcstores.com/store-mapper/"

	driver = SgSelenium().chrome()
	time.sleep(2)
	driver.get(base_link)
	time.sleep(randint(8,10))

	base = BeautifulSoup(driver.page_source,"lxml")
	
	data = []
	items = base.find(id="storemapper-list").find_all('li')

	for i, item in enumerate(items):
		logger.info("Link %s of %s" %(i+1,len(items)))
		locator_domain = "abcstores.com"
		location_name = item.h4.text.strip()
		logger.info(location_name)

		map_link = item.find(class_="storemapper_directions").a['href']
		driver.get(map_link)
		time.sleep(randint(8,10))
		map_base = BeautifulSoup(driver.page_source,"lxml")
		raw_address_line = map_base.find_all(class_="tactile-searchbox-input")[1]['aria-label'].replace("Destination","").strip()
		raw_address = raw_address_line.split(',')
		try:
			street_address = raw_address[0].strip()
			city = raw_address[1].strip()
			state = raw_address[2].split()[0].strip()
			try:
				zip_code = re.findall(r'[0-9]{5}', raw_address_line)[0]
			except:
				zip_code = "<MISSING>"
		except:
			street_address = item.find(class_="storemapper-address").text.strip()
			city = "<MISSING>"
			state = "<MISSING>"
			try:
				zip_code = re.findall(r'[0-9]{5}', raw_address_line)[0]
			except:
				zip_code = "<MISSING>"
		if state.isnumeric():
			state = "<MISSING>"
		if "ABC Store" in street_address or "Ritz Carlton" in street_address:
			street_address = city
			city = state
			state = "<MISSING>"
		if street_address == "Office Road":
			street_address = item.find(class_="storemapper-address").text.strip()
			city = "Lahaina"
			state = "HI"
			zip_code = "96761"
		if "building" in street_address.lower():
			raw_address = item.find(class_="storemapper-address").text.strip()
			street_address = raw_address[:raw_address.find(", Saipan")].strip()
			city = "Saipan"
			state = "Northern Mariana Islands"
			try:
				zip_code = re.findall(r'[0-9]{5}', raw_address)[0]
			except:
				zip_code = "<MISSING>"
		if street_address == "23 Fremont St":
			city = "Las Vegas"
			state = "NV"
			zip_code = "89101"
		if city == "Dededo" or city == "Tamuning" or city == "Tumon Bay":
			state = "Guam"
		if "Tumon" in city:
			city == "Tumon Bay"
			state = "Guam"
		country_code = "US"
		phone = item.find(class_="storemapper-phone").text.strip()
		location_type = "<MISSING>"
		try:
			hours_of_operation = item.find(class_="storemapper-custom-1").text.replace("~","-").replace("Hours:","").strip()
		except:
			hours_of_operation = "<MISSING>"
		try:
			store_number = re.findall(r'\#[0-9]{1,5}', location_name)[0][1:]
		except:
			store_number = "<MISSING>"

		lat = item.find(class_="storemapper-storelink")["data-lat"]
		longit = item.find(class_="storemapper-storelink")["data-lng"]

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, lat, longit, hours_of_operation])

	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
