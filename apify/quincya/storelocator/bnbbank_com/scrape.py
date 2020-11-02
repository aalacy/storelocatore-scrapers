from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bnbbank_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.bnbbank.com/branches-atms/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
		logger.info("Got today page")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	data = []

	items = base.find_all(class_="location small-12 medium-4 large-3 cell")
	locator_domain = "bnbbank.com"

	for item in items:
		link = "https://" + item.a["href"].split("//")[1]
		logger.info(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.h1.text.strip()

		street_address = base.find(class_="address_1").text.strip()
		city = base.find(class_="city").text.strip()
		state = base.find(class_="state").text.strip()
		zip_code = base.find(class_="zip").text.strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "Branch, " + base.find(id="location-info").find(class_="conveniences").text.replace("\n\n\n",",").replace("conveniences","").strip() 
		phone = base.find(id="main-info").find(class_="phone").text.strip()
		hours_of_operation = base.find(id="location-info").find(class_="main").text.replace("\n\n\n"," ").replace("Lobby Hours","").strip()
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		all_scripts = base.find_all('script')
		for script in all_scripts:
			if "LatLng" in str(script):
				script = str(script)
				lat_pos = script.find('LatLng') + 7
				latitude = script[lat_pos:script.find(',',lat_pos)].strip()
				long_pos = script.find(',',lat_pos) + 1
				longitude = script[long_pos:script.find(')',long_pos)-1].strip()
				break

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
