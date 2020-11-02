from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('myvue_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	link = "https://www.myvue.com/cinema/bromley/whats-on"

	driver = SgSelenium().chrome()
	time.sleep(randint(2,4))

	driver.get(link)
	time.sleep(randint(15,20))

	try:
		driver.find_element_by_css_selector('.select-cinema__trigger.icon-text.icon-filter-after').click()
		time.sleep(randint(4,6))
	except:
		driver.find_element_by_css_selector('.optanon-allow-all.accept-cookies-button').click()
		time.sleep(randint(4,6))
		driver.find_element_by_css_selector('.select-cinema__trigger.icon-text.icon-filter-after').click()

	base = BeautifulSoup(driver.page_source,"lxml") 
	items = base.find_all('a', attrs={'rv-html': "cinema.filteredname"})[1:]

	data = []
	fond_gps = []
	locator_domain = "myvue.com"

	for i, item in enumerate(items):
		logger.info("Link %s of %s" %(i+1,len(items)))
		link = "https://www.myvue.com/cinema/" + item['href'].split("/")[-2] + "/getting-here"
		link = link.replace("bury-the rock","bury-the-rock")
		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
			logger.info(link)
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		location_name = base.find(class_="select-cinema__wrapper").text.strip()

		raw_address = base.find(class_="container container--scroll").div.text.strip().split("\n")
		street_address = raw_address[-3].split(",")[0].strip()
		try:
			street_address = (raw_address[-4].strip() + " " + street_address).strip()
		except:
			pass
		state = "<MISSING>"
		city = raw_address[-2].strip()
		zip_code = raw_address[-1].strip()
		country_code = "GB"
		
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = "<MISSING>"

		hours_of_operation = "<MISSING>"
		geo = base.find("a",string="Get directions")['href'].split("=")[1].split(",")
		latitude = geo[0]
		longitude = geo[1]
		lat_long = latitude + "_" + longitude
		if lat_long in fond_gps:
			latitude = "<MISSING>"
			longitude = "<MISSING>"
		else:
			fond_gps.append(lat_long)

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
