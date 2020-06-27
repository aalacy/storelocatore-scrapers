from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re

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
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://store.ewingirrigation.com/locations/"

	driver = get_driver()
	time.sleep(2)

	print("Website loading..")
	driver.get(base_link)
	time.sleep(randint(2,4))

	element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
		(By.CLASS_NAME, "store_content")))

	print("Loaded!")
	time.sleep(randint(3,4))

	all_links = []

	results = driver.find_elements_by_class_name('store_content')

	for result in results:
		link = result.find_element_by_tag_name("a").get_attribute("data-url")
		if link not in all_links:
			all_links.append(link)

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	total_links = len(all_links)
	for i, link in enumerate(all_links):
		print("Link %s of %s" %(i+1,total_links))

		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(req.text,"lxml")
			print(link)
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		locator_domain = "ewingirrigation.com"
		location_name = "Ewing " + item.find('h2').text.strip()
		print(location_name)

		raw_address = item.find(class_='address').text.replace("\r\n\r\n","\n").split("\n")
		street_address = raw_address[0].strip()
		city_line = raw_address[-1].strip().split(',')
		city = city_line[0].strip()
		state = city_line[1].strip()
		zip_code = city_line[2].strip()
		if len(zip_code) > 5:
			if "-" not in zip_code:
				zip_code = zip_code[:5] + "-" + zip_code[5:]
		country_code = "US"

		store_number = item.find('input', attrs={'name': 'values'})['value']
		try:
			phone = item.find(class_='phone').text.replace('Phone:','').strip()
		except:
			phone = "<MISSING>"

		location_type = "<MISSING>"

		latitude = "<MISSING>"
		longitude = "<MISSING>"

		all_scripts = item.find_all('script')
		for script in all_scripts:
			if "latitude" in str(script):
				script = str(script)
				lat_pos = script.find('latitude') + 11
				latitude = script[lat_pos:script.find(',',lat_pos)-1]
				long_pos = script.find('longitude') + 12
				longitude = script[long_pos:script.find(',',long_pos)-1]
				if longitude == "-111.9":
					longitude = "-111.900"
				break

		raw_hours = item.find_all(class_="opening_hours_block")
		hours = ""
		hours_of_operation = ""

		try:
			for hour in raw_hours:
				hours = hours + " " + hour.text.replace("\xa0","").replace("\n"," ").replace("AM","AM ").replace("day","day ").strip()
			hours_of_operation = (re.sub(' +', ' ', hours)).strip()
		except:
			pass
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

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
