from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select


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

	base_link = "https://www.barlouie.com/locations"

	driver.get(base_link)
	time.sleep(randint(2,3))

	try:
		element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
			(By.ID, "address-input")))
		time.sleep(randint(1,2))
	except:
		print("Timeout waiting on page to load!")

	all_links = set()

	us_list = ['AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 
				'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MH', 'MA', 'MI', 'FM', 'MN', 'MS', 'MO', 'MT', 'NE', 
				'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PW', 'PA', 'PR', 'RI', 'SC', 
				'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'VI', 'WA', 'WV', 'WI', 'WY']

	for us_state in us_list:
		print("Searching " + us_state)
		search_element = driver.find_element_by_id("address-input")
		search_element.clear()
		time.sleep(randint(1,2))
		search_element.send_keys(us_state)
		time.sleep(randint(1,2))

		search_button = driver.find_element_by_class_name('zip-input').find_element_by_tag_name("button")
		driver.execute_script('arguments[0].click();', search_button)
		time.sleep(randint(2,4))
		try:
			element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
				(By.ID, "locations-target")))
			time.sleep(randint(1,2))
		except:
			print("Timeout waiting on results..skipping")
			continue

		while True:
			try:
				driver.find_element_by_id("load-more").click()
				time.sleep(randint(4,6))
			except:
				break

		base = BeautifulSoup(driver.page_source,"lxml")
		items = base.find_all(class_="location-card")
		print("Found %s items" %(len(items)))
		for item in items:
			all_links.add(item['id'] + "_https://www.barlouie.com" + item.find_all('a')[-1]['href'])

		
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	final_links = list(all_links)
	final_links.sort()
	for i, final_link in enumerate(final_links):
		print("Link %s of %s" %(i+1,len(final_links)))
		store_id = final_link.split("_")[0]
		final_link = final_link.split("_")[1]
		req = session.get(final_link, headers = HEADERS)
		print(final_link)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		script = base.find('script', attrs={'type': "application/ld+json"}).text.strip()
		store_data = json.loads(script)

		locator_domain = "barlouie.com"
		location_name = store_data['name'].replace("&#x27;","'")
		street_address = store_data['address']['streetAddress']
		city = store_data['address']['addressLocality']
		state = store_data['address']['addressRegion']
		zip_code = store_data['address']['postalCode']
		country_code = "US"
		store_number = store_id
		location_type = "<MISSING>"
		phone = store_data['telephone']
		latitude = store_data['geo']['latitude']
		longitude = store_data['geo']['longitude']
		hours_of_operation = " ".join(store_data['openingHours'])
		if not hours_of_operation:
			hours = base.find(class_="hours-group").find_all(class_="hour-container")
			for hour in hours:
				hours_of_operation = (hours_of_operation + " " + hour.text.replace("\n"," ").strip()).strip()

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
