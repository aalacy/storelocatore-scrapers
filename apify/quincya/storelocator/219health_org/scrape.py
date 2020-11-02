from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('219health_org')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://219health.org/locations/"

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

	items = items = base.find_all(class_="fl-row")[3:]
	locator_domain = "219health.org"

	for item in items:
		location_name = "<MISSING>"
		
		raw_address = str(item.p)
		raw_address = raw_address[raw_address.rfind('">')+2:].replace("</a>","").replace("</p>","").replace("p>","")
		if "<br/>" in raw_address:
			raw_address = raw_address.split("<br/>")
			street_address = raw_address[-2].strip()
			try:
				street_address = raw_address[-3].strip() + " " + street_address
			except:
				pass
			city = raw_address[-1].split(",")[0].strip()
			state = raw_address[-1].split(",")[1].split()[0].strip()
			zip_code = raw_address[-1].split(",")[1].split()[1].strip()
		else:
			raw_address = raw_address.replace(".",",").split(",")
			street_address = raw_address[0].strip()
			if "3432 169th St." in item.p.text:
				street_address = "3432 169th St."
			city = raw_address[-2].strip()
			state = raw_address[-1].split()[0].strip()
			zip_code = raw_address[-1].split()[1].strip()

		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		phone = item.find_all(class_="uabb-info-list-link")[1]['href'].replace("tel:","").replace("+2","+1-2")
		hours_of_operation = item.find_all(class_="uabb-info-list-description")[-1].text.replace("pm","pm ").replace("\xa0"," ").strip()

		map_link = item.a['href']
		if "@" in map_link:
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		else:
			req = session.get(map_link, headers = HEADERS)
			time.sleep(randint(1,2))
			try:
				maps = BeautifulSoup(req.text,"lxml")
			except (BaseException):
				logger.info('[!] Error Occured. ')
				logger.info('[?] Check whether system is Online.')

			try:
				raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
				latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
				longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
				if not longitude[5:8].isnumeric():
					raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
					latitude = raw_gps[raw_gps.rfind("=")+1:raw_gps.rfind(",")].strip()
					longitude = raw_gps[raw_gps.rfind("-"):].strip()
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
