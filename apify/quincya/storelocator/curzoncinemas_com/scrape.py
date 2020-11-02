from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json

from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('curzoncinemas_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.curzoncinemas.com/cinemas-list"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	driver = SgSelenium().chrome()
	time.sleep(2)

	data = []

	items = base.find_all(class_="cCinemasItemContent")
	locator_domain = "curzoncinemas.com"

	for item in items:

		link = "https://www.curzoncinemas.com" + item.a['href']
		logger.info(link)
		driver.get(link)
		time.sleep(randint(10,12))
		base = BeautifulSoup(driver.page_source,"lxml")

		script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
		store = json.loads(script)

		location_name = store['name']
		street_address = store['address']['streetAddress']
		city = store['address']['addressLocality']
		state = "<MISSING>"
		zip_code = store['address']['postalCode']
		country_code = store['address']['addressCountry']

		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = store['telephone']
		hours_of_operation = "<MISSING>"

		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
