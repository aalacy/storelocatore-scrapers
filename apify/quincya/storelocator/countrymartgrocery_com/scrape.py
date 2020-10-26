import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

import time
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('countrymartgrocery_com')




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
	
	base_link = "https://www.countrymartgrocery.com/my-store/store-locator"

	driver = get_driver()
	time.sleep(2)

	driver.get(base_link)
	time.sleep(2)

	wait = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                (By.CLASS_NAME, "fp-panel-item-wrapper")))

	data = []

	base = BeautifulSoup(driver.page_source,"lxml")
	items = base.find_all(class_="fp-panel-item-wrapper")

	locator_domain = "countrymartgrocery.com"

	for i in range(len(items)):
		item = items[i]
		location_name = item.find(class_='fp-link-secondary').text.strip()
		logger.info(location_name)

		location_type = "<MISSING>"

		raw_data = str(item.find(class_='fp-store-address')).replace("</div>","")
		raw_data = raw_data[raw_data.find(">")+2:].strip().split("<br/>")
		street_address = raw_data[0].strip()
		if len(raw_data) > 2:
			street_address = street_address + " " + raw_data[1].strip()
		city = raw_data[-1][:raw_data[-1].find(',')].strip()
		state = raw_data[-1][raw_data[-1].find(',')+1:raw_data[-1].rfind(' ')].strip()
		zip_code = raw_data[-1][raw_data[-1].rfind(' '):].strip()
		country_code = "US"
		store_number = item['data-store-number']
		
		try:
			phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", str(item))[0]
		except:
			phone = "<MISSING>"

		directions = driver.find_elements_by_css_selector(".fp-link-secondary.fp-link-directions")[i]
		# Open in new tab
		directions.send_keys(Keys.CONTROL + Keys.ENTER)
		time.sleep(2)
		new_tab = driver.window_handles[1]
		driver.switch_to.window(new_tab)
		time.sleep(5)

		try:
			map_link = driver.current_url
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"

		driver.close()
		driver.switch_to.window(driver.window_handles[0])

		try:
			hours = item.find(class_='fp-panel-store-hours').get_text(separator=u' ').replace("\n"," ").replace("\x96","").replace("  "," ").strip()
			hours_of_operation = re.sub(' +', ' ', hours)
		except:
			hours_of_operation = "<MISSING>"

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
