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
	
	base_link = "https://gcamplasma.com/gcam-locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find(class_="md:flex flex-row-reverse").ul.find_all("div")
	locator_domain = "gcamplasma.com"

	for item in items:

		try:
			location_name = item.h3.text.strip()
		except:
			continue

		if "coming" in location_name.lower():
			continue

		raw_address = item.p.text.replace(", USA","").replace("polis IN","polis, IN").split(",")

		street_address = " ".join(raw_address[:-2]).strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()
		city = raw_address[-2].strip()
		state = raw_address[-1].strip()[:-6].strip()
		zip_code = raw_address[-1][-6:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		latitude = item["data-markerlat"]
		longitude = item["data-markerlon"]

		link = item.find_all("a")[-1]["href"]

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		days = list(base.find(class_="wp-block-table pb-5 mb-8").tr.stripped_strings)
		hours = list(base.find(class_="wp-block-table pb-5 mb-8").find_all("tr")[-1].stripped_strings)

		hours_of_operation = ""
		for i in range(len(days)):
			hours_of_operation = (hours_of_operation + " " + days[i] + " " + hours[i]).strip()
		hours_of_operation = hours_of_operation.encode("ascii", "replace").decode().replace("?","-")

		phone = list(base.find(class_="wp-block-table alignwide is-style-stripes").stripped_strings)[-1]
		
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
