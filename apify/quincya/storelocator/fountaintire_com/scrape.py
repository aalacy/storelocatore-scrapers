from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json

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

	driver = SgSelenium().chrome()
	time.sleep(2)

	base_link = "https://www.fountaintire.com/store-finder"

	driver.get(base_link)
	time.sleep(randint(2,3))

	element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
		(By.ID, "locationAddress")))
	time.sleep(randint(1,2))

	#CA
	ca_list = ["AB", "BC", "SK", "NS", "MB", "QC", "ON", "NT", "PE", "NL", "NU", "YT"]

	all_links = set()
	for ca_state in ca_list:
		print("Searching " + ca_state)
		search_element = driver.find_element_by_id("locationAddress")
		search_element.clear()
		time.sleep(randint(1,2))
		search_element.send_keys(ca_state)
		time.sleep(randint(1,2))
		
		try:
			search_button = driver.find_element_by_id("locationForm").find_elements_by_xpath("//button[(@type='submit')]")[-1]
			search_button.click()
		except:
			try:
				search_button = driver.find_element_by_id("locationForm").find_elements_by_xpath("//button[(@type='submit')]")[-2]
				search_button.click()
			except:
				continue
		time.sleep(randint(4,6))
		try:
			element = WebDriverWait(driver, 100).until(EC.invisibility_of_element_located(
				(By.CSS_SELECTOR, ".loader.is-loading")))
			time.sleep(randint(2,4))
		except:
			print("Error processing..skipping")
			continue

		base = BeautifulSoup(driver.page_source,"lxml")
		items = base.find_all(class_="locationList-item")[1:]
		print("Found %s items" %(len(items)))
		for item in items:
			id_num = item['id'].split("-")[-1]
			all_links.add("https://www.fountaintire.com/stores/details/" + id_num)

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	final_links = list(all_links)
	final_links.sort()
	for i, final_link in enumerate(final_links):
		print("Link %s of %s" %(i+1,len(final_links)))
		print(final_link)
		req = session.get(final_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')
			
		locator_domain = "fountaintire.com"

		script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').replace("\r","").strip()
		store = json.loads(script)

		location_name = store['name']
		street_address = store['address']['streetAddress']
		city = store['address']['addressLocality']
		state = store['address']['addressRegion']
		zip_code = store['address']['postalCode']
		country_code = "CA"
		store_number = final_link.split("/")[-1]
		location_type = base.find(id="tab-features").text.strip().replace("\n",",")
		phone = store['telephone']

		hours_of_operation = ""
		raw_hours = store['openingHoursSpecification']
		for hours in raw_hours:
			day = hours['dayOfWeek']
			if len(day[0]) != 1:
				day = ' '.join(hours['dayOfWeek'])
			opens = hours['opens']
			closes = hours['closes']
			if opens != "" and closes != "":
				clean_hours = day + " " + opens + "-" + closes
				hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']
		page_url = store["url"]
		data.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
