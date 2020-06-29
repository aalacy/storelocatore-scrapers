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
	
	base_link = "https://www.flooranddecor.com/view-all-stores"

	driver = get_driver()
	time.sleep(2)

	driver.get(base_link)
	time.sleep(randint(8,10))

	states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
		"HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
		"MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
		"NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
		"SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

	all_links = []
	found_links = []

	for state in states:
		print("State: " + state)
		search_element = driver.find_element_by_id("dwfrm_storelocator_searchTerm")
		search_element.clear()
		time.sleep(randint(1,2))
		search_element.send_keys(state)
		time.sleep(randint(1,2))
		search_button = driver.find_element_by_class_name('btn-store-search')
		search_button.click()
		time.sleep(randint(4,6))

		results = driver.find_element_by_class_name('search-store-list').find_elements_by_tag_name("li")

		for result in results:
			item = result.find_element_by_class_name("store-actions")
			link = item.find_element_by_tag_name("a").get_attribute("href")
			try:
				result.find_element_by_css_selector(".fd-icon.fd-icon-map-marker.red.Normal.Store.Opened")
				location_type = "Current Store"
				if link not in found_links:
					found_links.append(link)
					all_links.append([link, location_type])
			except:
				try:
					result.find_element_by_css_selector(".fd-icon.fd-icon-map-marker.black.Design.Center.Opened")
					location_type = "Design Center"
					if link not in found_links:
						found_links.append(link)
						all_links.append([link, location_type])
				except:
					print("Skipping Upcoming store!")

	data = []
	total_links = len(all_links)
	for i, raw_link in enumerate(all_links):
		print("Link %s of %s" %(i+1,total_links))
		link = raw_link[0]

		driver.get(link)
		time.sleep(randint(2,4))

		try:
			element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
				(By.CLASS_NAME, "map")))
			time.sleep(randint(3,5))
			raw_gps = driver.find_element_by_xpath("//*[(@title='Open this area in Google Maps (opens a new window)')]").get_attribute("href")
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
			longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
		except:
			print('Timeout...')
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		item = BeautifulSoup(driver.page_source,"lxml")

		locator_domain = "flooranddecor.com"
		location_name = "Floor & Decor " + item.find('h1').text.strip()
		print(location_name)

		street_address = item.find('span', attrs={'itemprop': 'streetAddress'}).text.strip()
		city = item.find('span', attrs={'itemprop': 'addressLocality'}).text.replace(",","").strip()
		state = item.find('span', attrs={'itemprop': 'addressRegion'}).text.strip()
		zip_code = item.find('span', attrs={'itemprop': 'postalCode'}).text.strip()
		country_code = "US"

		store_number = link.split("=")[-1]
		try:
			phone = item.find('span', attrs={'itemprop': 'telephone'}).text.strip()
		except:
			phone = "<MISSING>"

		location_type = raw_link[1]

		raw_hours = item.find_all(class_="store-hours store-hours-1")
		hours = ""
		hours_of_operation = ""

		try:
			for hour in raw_hours:
				hours = hours + " " + hour.text.replace("\t","").replace("\n"," ").replace("PM","PM ").strip()
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
