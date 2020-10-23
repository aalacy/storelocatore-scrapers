from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('vanderbilts_com')



def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)

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
	
	base_link = "https://vanderbilts.com/retail-locations/"

	driver = get_driver()
	time.sleep(2)

	driver.get(base_link)
	time.sleep(randint(6,8))

	try:
		base = BeautifulSoup(driver.page_source,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	data = []
	items = base.find(id="wpsl-stores").find_all("li")
	for item in items:
		locator_domain = "vanderbilts.com"
		location_name = item.strong.text
		logger.info(location_name)

		street_address = item.find(class_="wpsl-street").text
		city_line = item.p.find_all("span")[1].text.split(",")
		city = city_line[0]
		state = city_line[1][:-6].strip()
		zip_code = city_line[1][-6:].strip()
		country_code = "US"
		store_number = item['data-store-id']
		location_type = "<MISSING>"
		phone = item.find(class_="wpsl-contact-details").a.text

		map_link = item.find(class_="wpsl-directions")['href']
		req = session.get(map_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			maps = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		try:
			raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
			longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		hours_of_operation = item.find(class_="wpsl-opening-hours").text.replace("PM","PM ").replace("day","day ").replace("  "," ").strip()

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
