from sgrequests import SgRequests
from sgselenium import SgSelenium
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rebounderz_com')



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
	
	base_link = "https://www.rebounderz.com/city/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find(class_="fl-row fl-row-fixed-width fl-row-bg-none fl-node-5cdf20eadb842").find_all(class_="fl-rich-text") + base.find(class_="fl-row fl-row-fixed-width fl-row-bg-none fl-node-5cdf2137cfbd7").find_all(class_="fl-rich-text")
	locator_domain = "rebounderz.com"

	for item in items:
		location_name = item.h3.text.strip()
		# logger.info(location_name)

		raw_address = item.p.text.split("\n")
		street_address = raw_address[0]
		city = raw_address[1].split(",")[0]
		state = raw_address[1].split(",")[1].split()[0]
		zip_code = raw_address[1].split(",")[1].split()[1]
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = item.find_all("p")[-2].text.replace("tel:","").strip()

		link = "https://www.rebounderz.com" + item.find_all("a")[-1]["href"]
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		hours_of_operation = base.find_all('div', {'class': re.compile(r'fl-col-group fl-node-.+fl-col-group-nested fl-col-group-custom-width')})[0].text.replace("\n", " ")
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
		hours_of_operation = hours_of_operation.replace("Munchkin and Me UNAVAILABLE","").replace("*Glow Night from 6PM to 10PM*","").replace("Munchkin and Me TBD","").strip()
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
		
		driver.get(link)
		time.sleep(randint(6,8))

		map_frame = driver.find_elements_by_tag_name("iframe")[0]
		driver.switch_to.frame(map_frame)
		time.sleep(randint(1,2))
		map_str = driver.page_source
		geo = re.findall(r'\[[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\]', map_str)[0].replace("[","").replace("]","").split(",")
		latitude = geo[0]
		longitude = geo[1]

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
