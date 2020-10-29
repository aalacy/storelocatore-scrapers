from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('gussbbq_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://gussbbq.com/"

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

	items = base.find_all(class_="ContainerGroup clearfix")[1].find_all("a")
	locator_domain = "gussbbq.com"

	for item in items:
		link = "https://gussbbq.com/" + item['href'] 
		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
			logger.info(link)
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		if "southpasadena" in link:
			location_name = base.find_all(class_='clearfix grpelem shared_content')[4].text.strip()
		else:
			location_name = base.find_all(class_='clearfix colelem shared_content')[0].text.strip()
		# logger.info(location_name)
		
		try:
			raw_address = base.find_all(class_='clearfix grpelem shared_content')[5].find_all('p')
			street_address = raw_address[1].text.strip()
			city_line = raw_address[2].text.split(",")
			city = city_line[0].strip()
			state = city_line[1].strip()[:-6].strip()
			zip_code = city_line[1][-6:].strip()
			phone = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', base.find_all(class_='clearfix grpelem shared_content')[5].text)[0]
			hours_of_operation = base.find_all(class_='rounded-corners clearfix grpelem shared_content')[3].text.replace("HOURS","").replace("\n"," ").strip()
		except:
			raw_address = base.find_all(class_='clearfix grpelem shared_content')[4].find_all('p')
			street_address = raw_address[1].text.strip()
			city_line = raw_address[2].text.split(",")
			if "Suite" in city_line[0]:
				street_address = street_address + " " + city_line[0]
				city_line = raw_address[3].text.split(",")
			city = city_line[0].strip()
			state = city_line[1].strip()[:-6].strip()
			zip_code = city_line[1][-6:].strip()
			phone = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', base.find_all(class_='clearfix grpelem shared_content')[4].text)[0]
			hours_of_operation = base.find_all(class_='rounded-corners clearfix grpelem shared_content')[1].text.replace("HOURS","").replace("\n"," ").strip()

		country_code = "US"
		store_number = "<MISSING>"
		
		location_type = "<MISSING>"

		all_scripts = base.find_all('script')
		for script in all_scripts:
			if "LatLng" in str(script):
				map_link = script.text.replace('\n', '').strip()
				break

		try:
			at_pos = map_link.find("LatLng")
			latitude = map_link[at_pos+7:map_link.find(",",at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(")", at_pos)].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
