from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
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
	
	base_link = "https://bohemian-studios.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")
	
	data = []

	items = base.find(class_="folder").find_all("a")
	locator_domain = "bohemian-studios.com"

	for item in items:
		link = "https://bohemian-studios.com" + item["href"]

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		if "permanently closed" in base.text:
			continue

		all_scripts = base.find_all('script')
		for script in all_scripts:
			if "mapLng" in str(script):
				script = str(script)
				break

		location_name = base.main.h1.text.strip()
		
		raw_address = list(base.h3.em.stripped_strings)
		
		street_address = raw_address[0].strip()
		city_line = raw_address[-1].strip().split(",")
		city = city_line[0].strip()
		state = city_line[-1].strip().split()[0].strip()
		zip_code = city_line[-1].strip().split()[1].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = "<MISSING>"

		geo = re.findall(r'mapLat"\:[0-9]{2}\.[0-9]+,"mapLng":-[0-9]{2,3}\.[0-9]+', script)[0]
		latitude = geo.split(",")[0].split(":")[1]
		longitude = geo.split(",")[1].split(":")[1]

		raw_hours = re.findall(r'"businessHours.+}]}}', script)[0]
		js = json.loads(raw_hours[16:])
		hours_of_operation = ""
		for day in js:
			hours_of_operation = (hours_of_operation + " " + day.title() + " " + js[day]['text']).strip()

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
