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
	
	base_link = 'https://www.winndixie.com/locator'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all(class_="details-link")
	locator_domain = "winndixie.com"

	for item in items:
		link = "https://www.winndixie.com" + item["href"]
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.h1.text.replace("\xa0"," ").strip()
				
		raw_address = list(base.find(class_="w-50 Mw-100").a.stripped_strings)
		street_address = raw_address[0].strip()
		if street_address[-1:] == ",":
			street_address = street_address[:-1]
		city = raw_address[-1].split(",")[0].strip()
		state = raw_address[-1].split(",")[1][:-6].strip()
		zip_code = raw_address[-1][-6:].strip()
		country_code = "US"
		store_number = link.split("search=")[1].split("&")[0]
		location_type = "<MISSING>"
		phone = base.find(class_="mob_num").text.strip()
		hours_of_operation = " ".join(list(base.find(class_="dis-inflex stores_head Mdis-blk w-100").find(class_="w-50 Mw-100").stripped_strings)).replace("Store hours","").strip()

		fin_script = ""
		all_scripts = base.find_all('script')
		for script in all_scripts:
			if "var locations" in str(script):
				fin_script = script.text.replace('\n', '').strip()
				break
		
		geo = re.findall(r'[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+',fin_script)[0].split(",")
		latitude = geo[0]
		longitude = geo[1]

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
