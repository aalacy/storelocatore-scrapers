from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('burgerville_com')



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

	driver = get_driver()
	time.sleep(2)

	all_links = set()

	states = ['Vancouver, WA', 'Orchards, WA', 'Longview, WA', 'Oakville, WA', 'Portland, OR', 'Tigard, OR', 'Gresham, OR', 'Brooks, OR']

	for state_search in states:
		base_link = "https://locations.burgerville.com/?q=%s" %(state_search)

		driver.get(base_link)
		time.sleep(randint(2,3))

		try:
			element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
				(By.CLASS_NAME, "result-list-inner")))
			time.sleep(randint(1,2))
		except:
			logger.info("Timeout waiting on results..skipping")

		base = BeautifulSoup(driver.page_source,"lxml")
		items = base.find(class_="result-list-inner").find_all(class_="name")

		for item in items:
			all_links.add(item.a['href'])

		
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	final_links = list(all_links)
	final_links.sort()
	for i, final_link in enumerate(final_links):
		logger.info("Link %s of %s" %(i+1,len(final_links)))
		req = session.get(final_link, headers = HEADERS)
		logger.info(final_link)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		script = base.find('script', attrs={'type': "application/ld+json"}).text.strip()
		store_data = json.loads(script)

		locator_domain = "burgerville.com"
		location_name = store_data['name']
		street_address = store_data['address']['streetAddress']
		city = store_data['address']['addressLocality']
		state = store_data['address']['addressRegion']
		zip_code = store_data['address']['postalCode']
		country_code = "US"
		store_number = store_data['@id']
		location_type = "<MISSING>"
		phone = store_data['telephone']
		latitude = store_data['geo']['latitude']
		longitude = store_data['geo']['longitude']
		hours_of_operation = base.find(class_="hours-body").text.replace("day","day ").replace("PM","PM ").replace("Closed","Closed ").strip()

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
