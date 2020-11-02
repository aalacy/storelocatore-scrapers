from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint

import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cineplex_com')




def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
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

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	all_links = []

	page_num = 1
	search_link = "https://www.cineplex.com/Theatres/TheatreListings?LocationURL=calgary&Range=5000&page=%s" %(page_num)

	req = session.get(search_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	last_page_num = int(base.find_all(class_="page-num")[-1].text)
	
	for page_num in range(1,last_page_num+1):
		search_link = "https://www.cineplex.com/Theatres/TheatreListings?LocationURL=calgary&Range=5000&page=%s" %(page_num)
		req = session.get(search_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
			logger.info(search_link)
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		results = base.find_all(class_="showtime-theatre")

		for result in results:
			link = "https://www.cineplex.com" + result.find(class_="theatre-text").a['href']

			if link not in all_links:
				all_links.append(link)

	data = []
	total_links = len(all_links)

	locator_domain = "cineplex.com"

	driver = get_driver()
	time.sleep(2)

	for i, link in enumerate(all_links):
		logger.info("Link %s of %s" %(i+1,total_links))
		time.sleep(randint(1,2))
		req = session.get(link, headers = HEADERS)

		try:
			item = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')
		
		location_name = item.find("h1").text.strip()
		raw_address = item.find(class_="margin-bot-sm").text.strip().split(",")
		street_address = " ".join(raw_address[:-3]).strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()
		city = raw_address[-3].strip()
		state = raw_address[-2].strip()
		zip_code = raw_address[-1].strip()
		country_code = "CA"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		try:
			phone = item.find(class_="theatre-details-page-phone col-sm-12 col-md-3").a.text.strip()
		except:
			phone = "<MISSING>"

		hours_of_operation = "<MISSING>"

		try:
			gmaps_link = item.find(class_="theatre-details-page-address margin-bot-xs col-sm-12 col-md-9").a['href']
			driver.get(gmaps_link)
			time.sleep(randint(8,10))

			map_link = driver.current_url
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"

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
