from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('junzi_kitchen')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.junzi.kitchen/visit"

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

	items = base.find(class_="col sqs-col-12 span-12").find_all(class_="row sqs-row")
	locator_domain = "junzi.kitchen"

	for item in items:

		location_name = item.div.strong.text
		logger.info(location_name)
		
		raw_address = json.loads(item.find_all("div")[-2]["data-block-json"])['location']
		street_address = raw_address['addressLine1']
		if street_address == "2896 Broadway":
			city = "<MISSING>"
			state = "NY"
			zip_code = "10025"
		else:
			city = raw_address['addressLine2'].split(",")[0].strip()
			state = raw_address['addressLine2'].split(",")[1].strip()
			zip_code = raw_address['addressLine2'].split(",")[2].strip()

		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = re.findall("[(\d)]{3}-[\d]{3}-[\d]{4}", str(item.p.text))[0]
		hours_of_operation = str(item.p).split("<br/>")[-3]
		if "am" not in hours_of_operation or "pm" not in hours_of_operation:
			hours_of_operation = str(item.p).split("<br/>")[-1].replace("</p>","")
		if "temporarily closed" in item.text:
			hours_of_operation = "temporarily closed"
		hours_of_operation = hours_of_operation.replace(" –","-").replace("–","-").replace(" - ","-")
		latitude = raw_address['mapLat']
		longitude = raw_address['mapLng']

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
