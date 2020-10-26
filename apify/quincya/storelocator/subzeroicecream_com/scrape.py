import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import csv
import re
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('subzeroicecream_com')





def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #return webdriver.Chrome(executable_path='driver/chromedriver', chrome_options=options)
    return webdriver.Chrome('chromedriver', chrome_options=options)


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "raw_address", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.subzeroicecream.com/find-location/c/0"

	driver = get_driver()
	driver.get(base_link)

	items = driver.find_elements_by_tag_name("gb-map-item-cell")
	actions = ActionChains(driver)
	actions.move_to_element(items[-1]).perform()
	time.sleep(5)
	items = driver.find_elements_by_tag_name("gb-map-item-cell")
	if len(items) < 50:
		items = driver.find_elements_by_tag_name("gb-map-item-cell")
		actions = ActionChains(driver)
		actions.move_to_element(items[-1]).perform()
	time.sleep(5)
	items = driver.find_elements_by_tag_name("gb-map-item-cell")

	logger.info(str(len(items)) + " links loaded..processing")

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	links = []
	for item in items:
		raw_link = item.find_element_by_tag_name("a").get_attribute("href")
		links.append(raw_link)

	driver.close()

	data = []
	for link in links:
		req = requests.get(link, headers=headers)
		try:
			base = BeautifulSoup(req.text,"lxml")
			time.sleep(3)
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		section = base.find('div', attrs={'class': 'content-container'})
					
		locator_domain = "subzeroicecream.com"
		try:
			location_name = section.find('h1').text.strip()
		except:
			location_name = base.title.text
		logger.info(location_name)

		raw_address = section.find('h3', attrs={'class': 'address ng-star-inserted'}).text.strip()
		street_address = "<INACCESSIBLE>"
		city = "<INACCESSIBLE>"
		state = location_name[location_name.rfind(",")+1:location_name.rfind("-")].strip()
		zip_code = "<MISSING>"
		country_code = "US"
		store_number = "<MISSING>"
		phone = base.find('ul', attrs={'class': 'buttons'}).a['href']
		phone = phone[phone.find(":")+1:]
		if len(phone) > 18:
			phone = "<MISSING>"
		location_type = "<MISSING>"
		latitude = base.find('meta', attrs={'property': 'place:location:latitude'})['content']
		longitude = base.find('meta', attrs={'property': 'place:location:longitude'})['content']
		hours_of_operation = "<MISSING>"

		data.append([locator_domain, location_name, raw_address, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
