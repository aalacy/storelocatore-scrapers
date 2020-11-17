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
	
	base_link = "https://www.rainforestcafe.com/store-locator/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
	stores = json.loads(script)['subOrganization']

	locator_domain = "rainforestcafe.com"

	for store in stores:
		location_name = store['name']
		if "england" in location_name.lower() or "france" in location_name.lower():
			continue
		street_address = store['address']['streetAddress']
		city = store['address']['addressLocality']
		state = store['address']['addressRegion']
		zip_code = store['address']['postalCode']
		country_code = "US"
		if not zip_code or "-" in zip_code:
			continue
		if " " in zip_code:
			country_code = "CA"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = store['telephone']

		link = store['url']

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		try:
			hours_of_operation = " ".join((base.find(id="intro").find_all("p")[1].stripped_strings)).split("Retail")[0].strip()
			if "-" not in hours_of_operation:
				hours_of_operation = " ".join((base.find(id="intro").find_all("p")[2].stripped_strings))
			latitude = base.find(class_="gmaps")['data-gmaps-lat']
			longitude = base.find(class_="gmaps")['data-gmaps-lng']
		except:
			hours_of_operation = "<MISSING>"
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
