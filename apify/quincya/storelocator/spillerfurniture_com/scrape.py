from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time

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
	
	base_link = "https://www.spillerfurniture.com/location.html"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)

	try:
		base = BeautifulSoup(req.text,"lxml")
		print("Got today page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	items = base.findAll('div', attrs={'class': 'StoreAddress'})

	driver = get_driver()
	time.sleep(2)

	data = []
	for item in items:
		locator_domain = "spillerfurniture.com"
		location_name = item.find(class_='location-name').text.strip()
		print(location_name)
		street_address = item.find(class_='location-address').text.strip()
		city = item.find(class_='location-city').text.strip()
		state = item.find(class_='location-state').text.strip()
		zip_code = item.find(class_='location-zipcode').text.strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = item.find(class_='location-phone').text.strip()
		location_type = "<MISSING>"
		hours_of_operation = "<MISSING>"

		gmaps_link = item.find('a')['href']
		driver.get(gmaps_link)
		time.sleep(7)

		try:
			map_link = driver.current_url
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"

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
