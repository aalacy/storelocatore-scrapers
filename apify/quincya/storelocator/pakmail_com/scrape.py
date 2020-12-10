from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
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
	
	base_link = 'https://www.pakmail.com/store-locator'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	items = base.find_all(class_="layout-3col blockish address-list")
	
	data = []
	locator_domain = "pakmail.com"

	for item in items:
		link = "https://www.pakmail.com" + item.a["href"]
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		try:
			script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
			store = json.loads(script)

			location_name = store['name']
			street_address = store['address']['streetAddress'].replace("Shopping Center","").split("(")[0].strip()
			city = store['address']['addressLocality']
			state = store['address']['addressRegion']
			zip_code = store['address']['postalCode']
			if len(zip_code) < 5:
				zip_code = "0" + zip_code
			phone = store['telephone']

			latitude = store['geo']['latitude']
			longitude = store['geo']['longitude']

			hours_of_operation = " ".join(list(base.find(class_="hours").stripped_strings))
			final_link = store['url']
		except:
			location_name = "Pak Mail " + item.h2.text.strip()
			street_address = list(item.find(class_="layout-3col__col-2").stripped_strings)[0].strip()
			city = item.h2.text.strip().split(",")[0]
			state = item.h2.text.strip().split(",")[1].strip()
			zip_code = list(item.find(class_="layout-3col__col-2").stripped_strings)[1][-5:].strip()
			phone = item.find(class_="layout-3col__col-3").text.split("[")[0].strip()
			final_link = req.url
			try:
				latitude = base.find('meta', attrs={'name': "geo.position"})['content'].split(";")[0]
				longitude = base.find('meta', attrs={'name': "geo.position"})['content'].split(";")[1]
				hours_of_operation = " ".join(list(base.find(id="block-views-store-hours-block-block").find(class_="view-content").stripped_strings))
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"
				hours_of_operation = "<MISSING>"
				final_link = base_link

		country_code = "US"
		store_number = link.split("/")[-1].split("US")[1]
		location_type = "<MISSING>"

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
