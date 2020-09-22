from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
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
	
	base_link = "https://paradisshopnsave.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find(class_="b2b-location-items-container").find_all("li")
	locator_domain = "paradisshopnsave.com"

	for item in items:
		location_name = item.h2.text.strip()
		
		raw_address = item['data-address'].split(", ,")
		street_address = raw_address[0].strip()
		city_line = raw_address[-1].split(",")
		city = city_line[0].strip()
		state = city_line[1].strip()
		zip_code = city_line[2].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = item.find_all("a")[-1]["href"].replace("tel:","")
		raw_hours = item.find(class_="b2b-location-detail-info").text
		hours_of_operation = raw_hours[raw_hours.find("Hours")+6:].replace("PM","PM ").strip()

		# Maps
		map_link = item.a["href"]
		req = session.get(map_link, headers = HEADERS)
		time.sleep(randint(1,2))
		maps = BeautifulSoup(req.text,"lxml")

		try:
			raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
			longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		if city == "Brewer":
			location_name = location_name + " - Brewer"
		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
