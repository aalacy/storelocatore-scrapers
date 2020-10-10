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
	
	base_link = 'https://c2b-services.bmw.com/c2b-localsearch/services/cache/v4/ShowAll?country=us&category=BD&clientid=UX_NICCE_FORM_DLO'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all("poi")
	locator_domain = "bmwmotorcycles.com"

	for item in items:

		location_name = item.find("name").text.strip()
		street_address = item.street.text.replace("12401Memorial","12401 Memorial").strip()
		if street_address[-1:] == ",":
			street_address = street_address[:-1]
		city = item.city.text.strip()
		try:
			state = item.state.text.split("/")[0].strip()
		except:
			if city == "Indianapolis":
				state = "IN"
			else:
				state = "<MISSING>"
		zip_code = item.postalcode.text.strip()
		country_code = item.countrycode.text.strip()
		store_number = item.agdealercode.text.split(",")[0].strip()
		location_type = "<MISSING>"
		phone = item.phone.text.strip()
		hours_of_operation = "<MISSING>"
		latitude = item.lat.text.strip()
		longitude = item.lng.text.strip()
		link = item.homepage.text.strip()
		if not link:
			link = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
