from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
	
	base_link = "https://livwell.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
		# print("Got today page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	data = []

	items = base.find_all(class_="post-details no-cut")
	locator_domain = "livwell.com"

	for i, item in enumerate(items):
		print(str(i+1) + " of " + str(len(items)))
		location_name = item.a.text.strip()
		print(location_name)
		
		raw_data = item.find(class_="post-description").find_all("p")
		street_address = raw_data[0].text.strip()
		city_line = raw_data[1].text
		city = city_line[:city_line.find(",")].strip()
		state = city_line[city_line.find(",")+1:city_line.find(",")+4].strip()
		zip_code = city_line[-6:].strip()

		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		try:
			phone =  re.findall("[[(\d)]{3}-[\d]{3}-[\d]{4}", str(item))[0]
		except:
			phone = "<MISSING>"

		hours_of_operation = raw_data[3].text.replace("Hours:","").strip()

		# Maps
		if street_address == "432 S Broadway":
			latitude = "39.7087123"
			longitude = "-105.0224345"
		else:
			map_link = raw_data[0].a['href']
			if "maps" in map_link:
				try:
					driver.get(map_link)
					time.sleep(randint(6,8))
					try:
						map_link = driver.current_url
						at_pos = map_link.rfind("@")
						latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
						longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
					except:
						latitude = "<INACCESSIBLE>"
						longitude = "<INACCESSIBLE>"
				except:
					latitude = "<MISSING>"
					longitude = "<MISSING>"
			else:
				latitude = "<MISSING>"
				longitude = "<MISSING>"

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
