from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

from sgselenium import SgSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.bncollege.com/campus-stores/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	driver = SgSelenium().chrome()
	time.sleep(2)

	data = []

	items = base.find(id="schools").find_all("li")
	locator_domain = "bncollege.com"

	poi_found = []
	for i, item in enumerate(items):
		link = item.a['href'].replace(".com%20",".com")
		if link == "https://depaul.bncollege.com/":
			link = "http://depaul-lincolnpark.bncollege.com/"
		if link in poi_found or link == "https://www.cpcc-harriscampusbookstore.com":
			continue
		else:
			poi_found.append(link)
		print("Link %s of %s" %(i+1,len(items)))
		print(link)
		
		try:
			req = session.get(link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")
		except:
			print("No results found..skipping")
			continue

		try:
			final_link = base.find(class_="mapInnerUl campusHours right wid44p").a['href']
		except:
			try:
				final_link = (req.url.split(".com/")[0] + ".com/" + base.find_all(class_="primaryBtn")[-1]['href']).replace(".com//",".com/")
			except:
				print("No results found..skipping")
				continue

		if final_link in poi_found:
			continue
		else:
			poi_found.append(final_link)

		store_number = final_link.split("=")[-1]

		driver.get(final_link)
		time.sleep(randint(2,4))

		try:
			element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
				(By.CLASS_NAME, "storeInfo")))
			time.sleep(randint(1,2))
		except:
			print("Timeout..no results found")
			continue

		final_link = driver.current_url
		base = BeautifulSoup(driver.page_source,"lxml")
		raw_data = base.find(class_="storeInfo").dl.text.strip().replace("\xa0"," ").split("\n")

		location_name = base.h3.text

		try:
			street_address = raw_data[-4].strip() + " " + raw_data[-3].strip()
		except:
			street_address = raw_data[-3].strip()

		if "PLEASE" in street_address:
			street_address = street_address[:street_address.find("PLEASE")].strip()

		raw_address = raw_data[-2].split(",")
		city = raw_address[0].strip()
		state = raw_address[-1].split()[0]
		zip_code = raw_address[1].split()[1]

		country_code = "US"
		location_type = "<MISSING>"
		phone = raw_data[-1]
		hours = base.find(class_="storeInfo").find_all("dl")[1].text.strip().replace("\t","").replace("\n"," ")
		hours_of_operation = (re.sub(' +', ' ', hours)).strip()
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
