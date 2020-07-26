from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint

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
	
	base_link = "https://www.saborcocinamexicana.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
		print("Got today page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	data = []

	raw_data = base.find(id="comp-k96idoil3inlineContent-gridContainer").p.text.split(",")
	locator_domain = "saborcocinamexicana.com"
	location_name = base.find(class_="color_11").text
	print(location_name)
	
	street_address = raw_data[0].strip()
	city = raw_data[1].strip()
	state = raw_data[2][:3].strip()
	zip_code = raw_data[2][3:].strip()

	country_code = "US"
	store_number = "<MISSING>"	
	location_type = "<MISSING>"

	try:
		phone =  base.find(id="comp-k96idoil3inlineContent-gridContainer").find_all('p')[-1].text
	except:
		phone = "<MISSING>"

	hours_of_operation = "<MISSING>"

	map_link = base.find(class_="lb1itemsContainer").a['data-content']

	driver.get(map_link)
	time.sleep(8)

	try:
		map_link = driver.current_url
		at_pos = map_link.rfind("@")
		latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
		longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
	except:
		latitude = "<INACCESSIBLE>"
		longitude = "<INACCESSIBLE>"

	data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
