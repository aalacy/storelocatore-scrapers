from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('veescafe_net')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.veescafe.net/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	data = []

	locator_domain = "veescafe.net"

	all_scripts = base.find_all('script')
	for script in all_scripts:
		if "latitude" in str(script):
			script = str(script)
			break
	raw_address = re.findall(r'{"siteDisplayName.+"businessSchedule', script)[0][:-18]
	raw_address = raw_address[raw_address.find('"street'):]
	raw_address = json.loads("{" + raw_address)

	location_name = base.title.text
	logger.info(location_name)

	street_address = raw_address['streetNumber'] + " " + raw_address['street']
	city = raw_address['city']
	state = 'CA'
	zip_code = raw_address['zip']

	country_code = "US"
	store_number = "<MISSING>"	
	location_type = "<MISSING>"
	raw_phone = base.find('a', attrs={'data-type': 'phone'}).text
	try:
		phone = re.findall("[\d]{3}-[\d]{3}-[\d]{4}", raw_phone)[0]
	except:
		phone = "<MISSING>"

	hours_of_operation = base.find(class_="txtNew").text.replace("We are open!","").replace("\xa0","").strip()
	latitude = raw_address['coordinates']['latitude']
	longitude = raw_address['coordinates']['longitude']

	data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
