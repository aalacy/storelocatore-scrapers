from sgrequests import SgRequests
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
from selenium.webdriver.common.keys import Keys


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
	
	base_link = "https://www.cookiedelivery.com/locations-deliveries.aspx?tab=3"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	time.sleep(randint(1,2))
	req = session.get(base_link, headers = HEADERS)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	items = base.find_all(class_='singlerowborder')
	cities = []
	for city in items:
		cities.append(city.text)

	search_link = "https://www.cookiedelivery.com/locations-deliveries.aspx?tab=2"
	driver = get_driver()
	time.sleep(2)

	driver.get(search_link)

	try:
		element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
			(By.CSS_SELECTOR, ".form-control.txtZipCode")))
		time.sleep(randint(1,2))
	except:
		print("Page failed to load")

	data= []
	found_poi = []
	for city in cities:
		print("Search: " + city)
		search_element = driver.find_element_by_css_selector(".form-control.txtZipCode")
		search_element.clear()
		time.sleep(randint(1,2))
		search_element.send_keys(city)
		time.sleep(randint(1,2))
		search_button = driver.find_elements_by_css_selector('.btn.btn-default')[1]
		driver.execute_script('arguments[0].click();', search_button)
		time.sleep(randint(2,4))

		try:
			element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
				(By.CSS_SELECTOR, ".location-store")))
			time.sleep(randint(1,2))
		except:
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		pois = driver.find_elements_by_css_selector('.location-store')
		driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
		time.sleep(randint(2,4))
		
		for i in range(len(pois)):
			pois = driver.find_elements_by_css_selector('.location-store')
			poi = pois[i]

			if poi.text in found_poi:
				continue
			else:
				found_poi.append(poi.text)

			try:
				poi.find_element_by_tag_name('a').click()
				time.sleep(randint(2,4))
			except:
				driver.find_element_by_tag_name('body').send_keys(Keys.ARROW_UP)
				time.sleep(randint(2,4))
				poi.find_element_by_tag_name('a').click()

			try:
				element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
					(By.ID, "locationOverview")))
				time.sleep(randint(1,2))
			except:
				print('[!] Error Occured. ')
				print('[?] Check whether system is Online.')

			base = BeautifulSoup(driver.page_source,"lxml")
			item = base.find(id="locationDetails")

			locator_domain = "cookiedelivery.com"
			location_name = item.find('h2').text.strip()
			print(location_name)

			raw_address = item.p.text.replace("\xa0"," ").strip().split("\n")
			if "<!" in raw_address[0]:
				raw_address.pop(0)
				raw_address.pop(0)

			street_address = raw_address[0].strip()
			city = raw_address[1].strip().split(",")[0].strip()
			state = raw_address[1].strip().split(",")[1][:-6].strip()
			zip_code = raw_address[1].strip().split(",")[1][-6:].strip()

			country_code = "US"
			store_number = "<MISSING>"
			phone = item.find_all("p")[2].text

			location_type = "<MISSING>"

			hours_of_operation = item.find_all("p")[1].text.replace("\n"," ").strip()

			raw_gps = item.a['href']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
			longitude = raw_gps[raw_gps.find(",")+1:].strip()

			data.append([locator_domain, search_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	
	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
