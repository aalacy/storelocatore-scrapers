import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.madison-reed.com/api/colorbar/getLocationsGroupedByRegion"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)

	base = BeautifulSoup(req.text,"lxml")
	stores = json.loads(base.text.strip())[0]

	data = []
	locator_domain = "madison-reed.com"

	for state in stores:
		state_stores = stores[state]
		for store in state_stores:
			opened = store['hasOpened']
			if not opened:
				continue
			location_name = store['neighborhood']			
			street_address = (store['address1'] + " " + store['address2']).strip()
			city = store['city'].strip()
			state = store['state']
			zip_code = store['zip']
			country_code = 'US'
			store_number = store['_id']
			location_type = "<MISSING>"
			phone = store['phone']
			hours = store['hours']
			hours_of_operation = ''
			for row in hours:
				day = row['day']
				closed = row['closed']
				if closed:
					hours_of_operation = hours_of_operation + " " + day + " Closed"
				else:
					hours_of_operation = hours_of_operation + " " + day + " " + row['open'] + "-" + row['close']
			hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
			latitude = store['coordinates']['lat']
			longitude = store['coordinates']['lon']
			link = 'https://www.madison-reed.com/colorbar/locations/' + store['code']
			# Store data
			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
