from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.alohaislandmart.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	found_poi = []
	found_links = []

	locator_domain = "alohaislandmart.com"

	items = base.find(class_="vce-row-content").find_all("a")

	main_links = []
	for item in items:
		main_links.append("https://www.alohaislandmart.com" + item['href'])

	final_links = []
	for main_link in main_links:
		req = session.get(main_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		items = base.find_all(class_="locationItem")
		for item in items:
			link = "https://www.alohaislandmart.com" + item.a['href']
			if link not in found_links:				
				final_links.append(link)
				found_links.append(link)

	for final_link in final_links:
		req = session.get(final_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		
		items = base.find_all('div', {'class': re.compile(r'locationIte.+')})
		for item in items:
			raw_data = item.div.find_all("div")

			location_name = item.h3.text.strip()
			if location_name in found_poi:
				continue
			found_poi.append(location_name)

			street_address = raw_data[0].text.strip()
			if street_address[-1:] == ",":
				street_address = street_address[:-1].strip()
			city_line = raw_data[1].text.strip().split(",")
			city = city_line[0].strip()
			state = city_line[-1].strip().split()[0].strip()
			zip_code = city_line[-1].strip().split()[1].strip()
			country_code = "US"
			store_number = "<MISSING>"

			location_type = ""
			raw_types = item.find_all(style="font-weight: bold;")
			for raw_type in raw_types:
				location_type = (location_type + ", " + raw_type.text.strip()).strip()
			location_type = location_type[1:].strip()
			if not location_type:
				location_type = "<MISSING>"

			phone = raw_data[2].text.strip()
			hours_of_operation = raw_data[3].text.replace("*","").replace("pm","pm ").strip()
			latitude = "<MISSING>"
			longitude = "<MISSING>"

			data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
