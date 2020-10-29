from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bevmo_com')



def get_driver():
	options = Options() 
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36")
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

	base_link = "https://www.bevmo.com/my-store/store-locator"

	driver = get_driver()
	time.sleep(2)

	driver.get(base_link)
	time.sleep(randint(6,8))

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	all_links = []
	base = BeautifulSoup(driver.page_source,"lxml")

	items = base.find_all(class_="fp-panel-item fp-store-info")
	for item in items:
		try:
			link = item.find(class_='fp-store-title').a['href']
			hours = item.find(class_="fp-panel-store-hours").p.text.replace("\n","").strip()
			all_links.append([link,hours])
		except:
			pass

	total_links = len(all_links)
	for i, raw_link in enumerate(all_links):
		link = raw_link[0]
		hours = raw_link[1]
		logger.info("Link %s of %s" %(i+1,total_links))

		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		locator_domain = "bevmo.com"

		location_name = item.find(class_='store-name').text.strip()
		if "(" in location_name and len(location_name) > 40:
			location_name = location_name[:location_name.find("(")].strip()
		logger.info(link)

		script = item.find_all('script', attrs={'type': "application/ld+json"})[1].text.strip()
		store = json.loads(script)

		street_address = store['address']['streetAddress']
		city = store['address']['addressLocality']
		state = store['address']['addressRegion']
		zip_code = store['address']['postalCode']

		country_code = "US"
		store_number = "<MISSING>"
		phone = store['telephone']

		location_type = "<MISSING>"

		hours_of_operation = hours

		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']

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
