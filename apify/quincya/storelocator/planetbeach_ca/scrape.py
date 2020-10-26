from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re

from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
	options = Options()
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-dev-shm-usage')
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
	
	base_link = "https://planetbeachcanada.com/store-locator/"

	driver = get_driver()
	driver.get(base_link)
	time.sleep(randint(8,10))

	sel_base = BeautifulSoup(driver.page_source,"lxml")
	results = sel_base.find(id="wpsl-stores").find_all('li')
	sel_items = []

	for sel_item in results:
		name = sel_item.strong.text.replace("St.Albert", "St. Albert")
		if name == "Saskatoon":
			name = "University Heights Saskatoon"
		num = sel_item['data-store-id']
		map_link = sel_item.a['href']

		sel_items.append([name,num,map_link])

	driver.close()

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	
	data = []

	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(2,4))

	try:
		base = BeautifulSoup(req.text,"lxml")
		print("Got main page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	items = base.find_all(class_="icon_description")

	for item in items:

		locator_domain = "planetbeachcanada.com"
		location_name = item.h4.text.strip()
		print(location_name)

		raw_address = item.p.text.strip().split("\n")

		street_address = raw_address[-3].strip()
		city_line = raw_address[-2].strip().split(",")
		city = city_line[0].strip()
		state = city_line[1][:3].strip()
		zip_code = city_line[1][3:].strip()

		country_code = "CA"

		phone = raw_address[-1].replace("Phone:","").strip()
		location_type = "<MISSING>"

		hours_of_operation = item.find_all("p")[-1].text.replace("\n"," ").strip()

		for sel_item in sel_items:
			if sel_item[0] == location_name:
				store_number = sel_item[1]
				map_link = sel_item[2]
				break

		if map_link:
			req = session.get(map_link, headers = HEADERS)
			time.sleep(randint(1,2))
			try:
				maps = BeautifulSoup(req.text,"lxml")
			except (BaseException):
				print('[!] Error Occured. ')
				print('[?] Check whether system is Online.')

			try:
				raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
				lat = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
				longit = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()

				if len(lat) < 5:
					lat = "<MISSING>"
					longit = "<MISSING>"
			except:
				lat = "<MISSING>"
				longit = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, lat, longit, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
