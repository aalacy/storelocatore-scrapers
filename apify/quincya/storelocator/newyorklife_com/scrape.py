from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
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
	
	base_link = "https://www.newyorklife.com/careers/go-directory"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	found_poi = []
	
	items = base.find_all('a', {'href': re.compile(r'careers/become-an-agent/')})
	locator_domain = "newyorklife.com"

	for item in items:
		link = "https://www.newyorklife.com" + item['href']
		if link in found_poi:
			continue
		found_poi.append(link)
		# print(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		script = base.find_all('script', attrs={'type': "application/ld+json"})[-1].text.strip()
		store = json.loads(script)

		location_name = "New York Life"
		street_address = store['address']['streetAddress'].strip()

		digit = re.search("\d", street_address).start(0)
		if digit != 0 and "THREE CITY PLACE" not in street_address.upper() and "BISHOP RANCH #3" not in street_address.upper() and "SOUTH TOWNE CORPORATE" not in street_address.upper():
			location_name = location_name + " - " + street_address[:digit].strip()
			street_address = street_address[digit:]
		if "THREE CITY PLACE" in street_address:
			location_name = location_name + " - CITY PLACE THREE"
			street_address = "THREE CITY PLACE DRIVE SUITE 690"
		if "BISHOP RANCH #3" in street_address:
			location_name = location_name + " - BISHOP RANCH #3"
			street_address = "2633 CAMINO RAMON SUITE 525"
		if "SOUTH TOWNE CORPORATE" in street_address:
			location_name = location_name + " - SOUTH TOWNE CORPORATE CENTER 1"
			street_address = "150 WEST CIVIC CENTER DRIVE SUITE 600"

		city = store['address']['addressLocality'].strip()
		state = store['address']['addressRegion'].strip()
		zip_code = store['address']['postalCode'].strip()
		country_code = store['address']['addressCountry'].strip()
		store_number = "<MISSING>"
		phone = store['telephone']
		location_type = "<MISSING>"
		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']
		hours_of_operation = "<MISSING>"

		data.append([locator_domain, link, location_name.upper(), street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
