from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re

from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cpk_com')




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
	
	base_link = "https://www.cpk.com/Location/Stores"

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

	for state in states:
		logger.info("State: " + state)
		search_element = driver.find_element_by_id("Address2")
		search_element.clear()
		time.sleep(randint(1,2))
		search_element.send_keys(state)
		time.sleep(randint(1,2))
		search_button = driver.find_element_by_id('btnFind2')
		driver.execute_script('arguments[0].click();', search_button)
		time.sleep(randint(6,8))

		# Try to zoom out to load all results
		try:
			zoom_out = driver.find_element_by_xpath("//button[(@aria-label='Zoom out')]")
			driver.execute_script('arguments[0].click();', zoom_out)
			time.sleep(randint(6,8))
		except:
			pass

		results = driver.find_element_by_id('ResultList').find_elements_by_class_name("Result")

		for result in results:
			raw_link = result.find_element_by_class_name("Direction").find_element_by_tag_name("input").get_attribute("onclick")
			link = "https://www.cpk.com" + raw_link.split("'")[1].strip()

			if link not in all_links:
				all_links.append(link)

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	total_links = len(all_links)
	for i, link in enumerate(all_links):
		logger.info("Link %s of %s" %(i+1,total_links))
		time.sleep(randint(1,2))
		req = session.get(link, headers = HEADERS)

		try:
			item = BeautifulSoup(req.text,"lxml")
			logger.info("Got today page")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		locator_domain = "cpk.com"
		location_name = item.find(class_='StoreName').text.strip()
		logger.info(location_name)

		raw_data = str(item.find(class_="Address")).replace("</div>","").replace("<br/>"," ")
		raw_data = raw_data[raw_data.find(">")+3:].strip().split('\n')
		street_address = raw_data[0].replace("Dallas, TX 75216","").strip()
		city = raw_data[-1][:raw_data[-1].find(',')].strip()
		state = raw_data[-1][raw_data[-1].find(',')+1:raw_data[-1].rfind(' ')].strip()
		zip_code = raw_data[-1][raw_data[-1].rfind(' ')+1:].strip()
		if len(zip_code) < 5:
			zip_code = "0" + zip_code
		country_code = "US"

		store_number = "<MISSING>"
		try:
			phone = item.find(class_='Phone').text.replace("Phone :","").strip()
		except:
			phone = "<MISSING>"

		location_type = "<MISSING>"
		raw_hours = item.find_all(class_="DayOfWeek")

		hours = ""
		hours_of_operation = ""

		try:
			for hour in raw_hours:
				hours = hours + " " + hour.text.strip()
			hours_of_operation = (re.sub(' +', ' ', hours)).strip()
		except:
			pass
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		try:
			map_link = item.find(id="map_canvas").find("img")['src']
			latitude = map_link[map_link.rfind("|")+1:map_link.rfind(",")].strip()
			longitude = map_link[map_link.rfind(",")+1:].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		try:
			int(latitude[4:8])
		except:
			latitude = "<MISSING>"

		try:
			int(longitude[6:8])
		except:
			longitude = "<MISSING>"

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
