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
	
	base_link = 'http://www.philsonestop.com/locations.html'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all(class_="neo-asset-inner mCS_destroyed")
	locator_domain = "philsonestop.com"

	for item in items:
		if "Corporate Office" in str(item):
			continue

		location_name = item.p.text.strip().encode("ascii", "replace").decode().replace("?","")
		
		raw_address = item.find_all("p")[1].text.split(",")
		street_address = raw_address[0].strip()
		city = raw_address[1].strip()
		state = raw_address[-1].split()[0].strip()
		if state.isnumeric():
			state = raw_address[-2].strip()
			zip_code = raw_address[-1].strip()
		else:
			try:
				zip_code = raw_address[-1].split()[1].strip()
			except:
				zip_code = "<MISSING>"
		country_code = "US"
		store_number = location_name.split("#")[-1][:2].strip()
		location_type = "<MISSING>"
		phone = item.find_all("p")[2].text.replace("Phone:","").strip()
		hours_of_operation = item.ul.text.strip().replace("\n"," ").strip().encode("ascii", "replace").decode().replace("?","").replace("!","")
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state.upper(), zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
