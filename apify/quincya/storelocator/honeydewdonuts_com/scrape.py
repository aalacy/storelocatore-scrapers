from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.honeydewdonuts.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers=headers)
	base = BeautifulSoup(req.text,"lxml")

	items = base.find(class_="col-md-3").find_all("script")[:-1]

	data = []
	for item in items:
		locator_domain = "honeydewdonuts.com"

		raw_text = item.text.replace('\r\n', '').replace(':','":"').replace(',','",').replace('" "','"').replace('""','"').replace('   ','"').strip()
		raw_text = (re.sub('"+', '"', raw_text)).strip()
		script = raw_text[raw_text.find("=")+1:raw_text.rfind("}")+1].replace('"phone":",','"phone":"",')
		store = json.loads(script)

		location_name = store['name']
		street_address = store['address']
		city = store['city']
		state = store['state']
		zip_code = store['zipCode']
		country_code = "US"
		phone = store['phone']
		if not phone:
			phone = "<MISSING>"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		hours_of_operation = "<MISSING>"
		latitude = store['latitude'].strip()
		longitude = store['longitude'].strip()

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
