from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re
from random import randint

from sgselenium import SgSelenium

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.copart.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	driver = SgSelenium().chrome()
	time.sleep(2)

	driver.get(base_link)
	time.sleep(randint(2,4))

	try:
		base = BeautifulSoup(driver.page_source,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	items = base.find_all('a', attrs={'data-uname': "USALocationLinks"})
	
	all_links = []
	for item in items:
		link = "https://www.copart.com/" + item['href'].replace("./","")
		all_links.append(link)

	data = []
	total_links = len(all_links)
	for i, link in enumerate(all_links):
		print("Link %s of %s" %(i+1,total_links))
		print(link)
		
		driver.get(link)
		time.sleep(randint(2,4))

		try:
			element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
				(By.CLASS_NAME, "loc-detail-infofix")))
			time.sleep(randint(1,2))
		except:
			print("Timeout..no results found")
			continue

		item = BeautifulSoup(driver.page_source,"lxml")

		locator_domain = "copart.com"
		
		location_name = item.find('title', attrs={'ng-bind-html': "title"}).text.replace("100% Online Car Auctions -","").strip()
		# print(location_name)

		raw_address = item.find(class_='location-yard-address').p.text[3:].replace(",\n\t",",").replace("\n\t",",").replace("\t","").strip().split(",")

		street_address = raw_address[0].strip()
		city = raw_address[1].strip()
		state = raw_address[2].strip()
		zip_code = raw_address[3].strip()

		if " " not in zip_code[:5]:
			country_code = "US"
			zip_code = zip_code.replace(" ", "-")
		else:
			country_code = "CA"

		raw_phone = item.find(class_="locations-desc row no-margin").text.strip()
		phone = raw_phone[raw_phone.find("Phone:")+6:raw_phone.find("Phone:")+22].strip()
		if not phone[-4:].isnumeric():
			phone = "<MISSING>"

		location_type = "<MISSING>"

		raw_hours = item.find(class_="row no-margin loc-detail-infofix").text.replace("Hours","").strip()
		hours_of_operation = raw_hours[:raw_hours.find("Directions")].replace("\n"," ").strip()

		store_number = link.split("-")[-1].replace("/","")

		# Get lat/long
		map_link = item.find('a', attrs={'data-uname': "direction"})['href']

		req = session.get(map_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			maps = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')
		
		try:
			raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
			longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

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
