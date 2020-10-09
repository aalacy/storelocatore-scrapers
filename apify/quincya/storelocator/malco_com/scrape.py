from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://malco.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	found_poi = []
	items = base.find(id="theatre_table").find_all("a")
	locator_domain = "malco.com"

	for item in items:
		link = base_link + item["href"]
		if link in found_poi:
			continue
		found_poi.append(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.h5.text.strip()
		# print(link)
		
		raw_data = list(base.find(class_="w3-half").stripped_strings)
		
		street_address = raw_data[1].strip()
		if "206 Commonwealth Blvd" in street_address:
			street_address = "206 Commonwealth Blvd"
		city_line = raw_data[2].split(",")
		city = city_line[0].strip()
		state = city_line[-1].strip()[:-6].strip()
		zip_code = city_line[-1][-6:].strip()
		country_code = "US"
		store_number = link.split("=")[-1]
		location_type = "<MISSING>"
		phone = raw_data[-1].strip()
		hours_of_operation = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
