from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re
import json

from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
	
	base_link = "https://99only.com/stores/near-me"

	driver = get_driver()
	time.sleep(2)

	driver.get(base_link)
	time.sleep(randint(8,10))

	all_links = []

	for i in range(8):
		# Try to zoom out to load all results
		try:
			zoom_out = driver.find_element_by_xpath("//button[(@aria-label='Zoom out')]")
			driver.execute_script('arguments[0].click();', zoom_out)
			time.sleep(randint(i+3,i+5))
		except:
			pass

	time.sleep(randint(5,8))
	results = driver.find_elements_by_css_selector('.overlay-link.view-store-store-tile')

	for result in results:
		link = result.get_attribute('href')

		if link not in all_links:
			all_links.append(link)

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	total_links = len(all_links)
	for i, link in enumerate(all_links):
		print("Link %s of %s" %(i+1,total_links))
		time.sleep(randint(1,2))
		req = session.get(link, headers = HEADERS)

		try:
			item = BeautifulSoup(req.text,"lxml")
			print(link)
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		script_str = str(item.find('script', attrs={'type': 'application/ld+json'}))
		script = script_str[script_str.find("["):script_str.rfind("]")+1]
		js = json.loads(script)[0]

		locator_domain = "99only.com"
		location_name = item.find('h1').text.strip()
		# print(location_name)

		street_address = js['address']['streetAddress']
		city = js['address']['addressLocality']
		state = js['address']['addressRegion']
		zip_code = js['address']['postalCode']

		country_code = "US"
		store_number = item.find(class_="store-number").text.replace("#","").strip()
		phone = "<MISSING>"

		location_type = "<MISSING>"

		raw_hours = item.find(class_="store-hours-list").find_all('tr')[1:]
		hours = ""
		hours_of_operation = ""

		try:
			for hour in raw_hours:
				hours = hours + " " + hour.text.replace("\t","").replace("\n"," ").strip()
			hours_of_operation = (re.sub(' +', ' ', hours)).strip()
		except:
			pass
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		latitude = js['geo']['latitude']
		longitude = js['geo']['longitude']

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
