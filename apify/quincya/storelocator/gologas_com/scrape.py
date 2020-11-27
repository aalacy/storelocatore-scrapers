from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
import json
from sgselenium import SgChrome

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://www.gologas.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find(id="x-section-2").find_all("a")
	locator_domain = "gologas.com"

	driver = SgChrome().chrome()

	for item in items:
		try:
			link = item["href"]
		except:
			continue
			
		driver.get(link)
		
		base = BeautifulSoup(driver.page_source,"lxml")

		locs = base.find_all('div', {'class': re.compile(r'wpgmaps_mlist_row wpgmza_basic_row wpgmaps_.+')})

		for loc in locs:
			location_name = base.h2.text.strip()
			raw_address = loc.find(class_="wpgmza-address").text
			location_name = base.h2.text.strip()
			if "," in location_name:
				city = location_name.split(",")[0].strip()
				state = location_name.split(",")[1][:3].strip()
			else:
				city = location_name.split("|")[0].strip()
				state = raw_address.split(",")[-1][:3].strip()
				
			street_address = raw_address[:raw_address.rfind(city)].strip()
			if street_address[-1:] == ",":
				street_address = street_address[:-1]
			try:
				zip_code = re.findall(r'[0-9]{5}',raw_address[-20:])[0]
			except:
				zip_code = "<MISSING>"
			country_code = "US"
			store_number = "<MISSING>"
			icon = loc.find(class_="wpgmza_marker_icon")["src"]
			if "savemarker" in icon:
				location_type = "Save"
			elif "allstarmarker" in icon:
				location_type = "AllStar"
			elif "golomarker" in icon:
				location_type = "GoLo"
			else:
				location_type = "<MISSING>"
			phone = "<MISSING>"
			hours_of_operation = "<MISSING>"
			latitude = loc['data-latlng'].split(",")[0].strip()
			longitude = loc['data-latlng'].split(",")[1].strip()

			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
