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
	
	base_link = "http://www.bfscompanies.com/locations.php?state=&type=BFS%20Foods"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	all_scripts = base.find_all('script')
	for script in all_scripts:
		if "LatLng" in str(script):
			script = str(script)
			break

	raw_data = script.split("var positions;")[-1].split("map.setCenter")[0].strip()
	items = raw_data.split("var myLatlng")[1:]

	locator_domain = "bfscompanies.com"

	for item in items:

		location_name = re.findall(r'title.+', item)[0].replace('title:','').strip()[1:-1]

		raw_address = re.findall(r'<p>.+ \"\+', item)[0].replace('"+','').replace('<p>','').strip()
		raw_street = " ".join(raw_address.split(",")[:-1]).strip()
		street_address = " ".join(raw_street.split()[:-1]).strip()
		city = raw_street.split()[-1].strip()

		if "Mt." in street_address:
			city = street_address[street_address.rfind("Mt."):].strip() + " " + city
			street_address = street_address[:street_address.rfind("Mt.")].strip()
		elif city in ["Mills","City","Castle","Rock","Alta","Hall"]:
			street_address = " ".join(raw_street.split()[:-2]).strip()
			city = " ".join(raw_street.split()[-2:]).strip()
		
		state = raw_address[-8:-6].strip()
		zip_code = raw_address[-6:].strip()
		if " 2654" in zip_code:
			zip_code = "26554"
			state = "WV"
		
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		try:
			phone = re.findall("[\d]{3}-[\d]{3}-[\d]{4}", str(item))[0]
		except:
			phone = "<MISSING>"

		hours_of_operation = "<MISSING>"
		geo = re.findall(r'[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+', item)[0].split(",")
		latitude = geo[0]
		longitude = geo[1]

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
