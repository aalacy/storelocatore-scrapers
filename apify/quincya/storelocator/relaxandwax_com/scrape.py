from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.relaxandwax.com/JS/salons.js"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	js = base.text[14:].strip().replace("//","")
	stores = json.loads(js)

	locator_domain = "relaxandwax.com"

	for store in stores:
		location_name = store['name']
		street_address = store['address'].replace("\r\n"," ")
		city = store['city']
		state = store['state']
		zip_code = store['zip']
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = store['tel']
		hours_of_operation = ""
		raw_hours = store['hours']
		for row in raw_hours:
			hours = row['day'] + " " + row['hours']
			hours_of_operation = (hours_of_operation + " " + hours).strip()
		latitude = store['lat']
		longitude = store['lon']
		if street_address == "2824 Cole Avenue":
			latitude = "32.8015449"
			longitude = "-96.8374904"
		link = "https://www.relaxandwax.com/" + store['url']
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
