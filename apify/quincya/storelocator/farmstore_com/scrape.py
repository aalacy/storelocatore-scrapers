from bs4 import BeautifulSoup
import csv
import time
from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


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

	base_link = "https://www.farmstore.com/locations"

	print("Loading page ..")
	driver.get(base_link)
	time.sleep(randint(2,3))

	try:
		element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
			(By.ID, "retail-panel")))
		time.sleep(randint(2,4))
	except:
		print("Timeout waiting on page to load!")

	data = []

	base = BeautifulSoup(driver.page_source,"lxml")
	items = base.find_all(class_="retail-result result row")
	print("Found %s items" %(len(items)))
	for item in items:
		locator_domain = "farmstore.com"
		location_name = item.find(class_="store-name").text
		raw_address = str(item.find(class_="address"))
		raw_address = raw_address[raw_address.find('>')+1:raw_address.rfind('<')].split('<br/>')
		street_address = raw_address[0].strip()
		city = raw_address[1].split(',')[0].strip()
		state = raw_address[1].split(',')[1][:4].strip()
		zip_code = raw_address[1].split(',')[1][-6:].strip()
		country_code = "US"
		store_number = item['id'].split('_')[1]
		location_type = "<MISSING>"
		phone = item.find(class_="phone").text.replace("Phone:","").strip()
		latitude = item['data-lat']
		longitude = item['data-lng']
		hours_of_operation = item.find(class_="hours").text.replace("\n"," ").strip()
		if not hours_of_operation:
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
