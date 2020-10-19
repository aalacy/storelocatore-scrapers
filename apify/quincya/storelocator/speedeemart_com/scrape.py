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
	
	base_link = "https://speedeemart.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find(class_="et_pb_section et_pb_section_3 et_section_regular").find_all("p")
	locator_domain = "speedeemart.com"

	for item in items:

		raw_data = list(item.stripped_strings)
		try:
			location_name = raw_data[0].strip()
		except:
			continue
		
		if ", " in raw_data[2]:
			city_num = 2
		elif ", " in raw_data[3]:
			city_num = 3

		street_address = " ".join(raw_data[1:city_num]).strip()
		city = raw_data[city_num].split(",")[0].strip()
		state = raw_data[city_num].split(",")[1].strip()
		zip_code = raw_data[city_num+1].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = raw_data[city_num+2].strip()
		hours_of_operation = " ".join(raw_data[city_num+3:]).strip()
		if "(" not in phone:
			phone = "<MISSING>"
			hours_of_operation = " ".join(raw_data[city_num+2:]).strip()
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
