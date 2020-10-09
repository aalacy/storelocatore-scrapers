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
	
	base_link = "https://www.expressmartstores.com/locations.html"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find(class_="locations").find_all("h4")
	locator_domain = "expressmartstores.com"

	for item in items:
		link = "https://www.expressmartstores.com" + item.a["href"]
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.find(class_="phone clearfix").h2.text.strip()
		# print(location_name)
		
		raw_address = str(base.find(class_="address clearfix").p).split("<br/>")

		street_address = raw_address[0][3:].strip()
		city_line = raw_address[-1][:-4].strip().split(",")
		city = city_line[0][:-3].strip()
		state = city_line[0][-3:].strip()
		zip_code = city_line[-1].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = base.find(class_="row columns primaryContent clearfix").ul.text.strip().replace("\n",",")
		phone = base.find(class_="phone clearfix").h3.text.strip()
		hours_of_operation = base.find(class_="hours clearfix").p.text.replace("Hours:","").replace("pm","pm ").strip()

		try:
			map_link = base.find(title="Need Directions")["href"]
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
