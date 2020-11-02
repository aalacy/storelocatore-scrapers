from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tljus_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.tljus.com/store-sitemap.xml"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items=base.find_all("loc")[1:]
	locator_domain = "tljus.com"

	for item in items:
		link = item.text
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.find('meta', attrs={'property': "og:title"})['content']
		logger.info(location_name)
		
		raw_data = base.find('meta', attrs={'property': "og:description"})['content'].replace("(Inside H-mart)","").replace("Blvd Houston","Blvd, Houston").replace("Blvd, #A","Blvd #A,")\
		.replace("G 202","G 202,").replace("–","-").replace("Doraville GA","Doraville, GA").replace("IL, ","IL ").replace("#107","#107,").replace("B-115","B-115,")
		tel = ""
		if " T." in raw_data:
			tel = " T."
		elif " T:" in raw_data:
			tel = " T:"
		if tel:
			phone = raw_data[raw_data.find(tel)+3:].strip()
			raw_data = raw_data[:raw_data.find(tel)].strip()
		else:
			phone = "<MISSING>"

		raw_address = raw_data.split(",")
		if len(raw_address) == 2:
			raw_address = raw_data.replace(".",",").split(",")
		
		street_address = " ".join(raw_address[:-2]).strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()
		city = raw_address[-2].strip()
		state = raw_address[-1].strip()[:-6].strip()
		zip_code = raw_address[-1][-6:].strip()
		if not zip_code.isnumeric():
			state = zip_code
			zip_code = "<MISSING>"
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		hours_of_operation = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
