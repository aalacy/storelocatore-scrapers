from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re

from random import randint
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('freshiesdeli_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://freshiesdeli.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	all_links = []
	data = []

	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(2,4))

	try:
		base = str(BeautifulSoup(req.text,"lxml"))
		logger.info("Got main page")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	all_links = re.findall( r"https://www.freshiesdeli.com/storelocations/[a-z]+",base)

	total_links = len(all_links)
	for i, link in enumerate(all_links):
		logger.info("Link %s of %s" %(i+1,total_links))

		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		locator_domain = "freshiesdeli.com"

		location_name = item.find('meta', attrs={'property': "og:title"})['content'].replace("—","-")
		if location_name == "Freshies Deli" and link == "https://www.freshiesdeli.com/storelocations/machiasfreshies":
			link = "https://freshiesdeli.com/storelocations/machaisfreshies"
			req = session.get(link, headers = HEADERS)
			time.sleep(randint(1,2))
			try:
				item = BeautifulSoup(req.text,"lxml")
				location_name = item.find('meta', attrs={'property': "og:title"})['content'].replace("—","-")
			except (BaseException):
				logger.info('[!] Error Occured. ')
				logger.info('[?] Check whether system is Online.')

		logger.info(location_name)
		
		phone = item.find('meta', attrs={'itemprop': "description"})['content'][-15:].strip()
		if "(" not in phone:
			phone = item.find('meta', attrs={'itemprop': "description"})['content'][3:18].strip()
			raw_address = item.find('meta', attrs={'itemprop': "description"})['content'][20:].replace("St ","St. ").replace("Trail ","Trail. ").replace("","").strip()
		else:
			raw_address = item.find('meta', attrs={'itemprop': "description"})['content'][3:-18].replace("St ","St. ").replace("Trail ","Trail. ").replace("","").strip()
		street_address = raw_address[:raw_address.find(".")]
		city = raw_address[raw_address.find(".")+1:raw_address.find(",")].strip()
		state = raw_address[-3:].strip()
		zip_code = "<MISSING>"

		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		hours_of_operation = ""
		raw_hours = item.find_all(class_="sqs-block-content")[3].find_all("tr")[1:]
		if not raw_hours:
			raw_hours = item.find_all(class_="sqs-block-content")[2].find_all("tr")[1:]
		for raw_hour in raw_hours:
			day = raw_hour.td.text
			hours = raw_hour.find_all("td")[2].text
			hours_of_operation = hours_of_operation + " " + day + " " + hours
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		all_scripts = item.find_all('script')
		for script in all_scripts:
			if "LatLng" in str(script):
				script = str(script)
				lat_pos = script.find('LatLng') + 7
				latitude = script[lat_pos:script.find(',',lat_pos)-1]
				longitude = script[script.find(',',lat_pos)+1:script.find(')',lat_pos)]
				break

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
