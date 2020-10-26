from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time

from random import randint


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://www.lonestarfoodstores.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	locator_domain = "lonestarfoodstores.com"

	data = []
	city_list = []
	cities = base.find_all(class_="font_0")
	for city in cities:
		city_list.append(city.text.replace("Stores","").replace("Store","").strip())

	rows = base.find_all(class_="font_8")

	for i, raw_row in enumerate(rows):
		row = raw_row.text
		if "(903) 893-8781" in row:
			row = "Phone: " + row

		if "Lone Star #" in row:
			# New POI
			location_name = row.replace("\u200b","").strip()
			print(location_name)
			store_number = location_name[location_name.find("#")+1:location_name.find("#")+3]
			raw_address = rows[i+1].text
			if "," not in raw_address:
				raw_address = raw_address + " " + rows[i+2].text
			state = raw_address[raw_address.rfind(",")+1:raw_address.rfind(",")+4].strip()
			zip_code = raw_address[-6:].strip()
			if not zip_code.isnumeric():
				zip_code = rows[i+1].text[:5].strip()
			if not zip_code.isnumeric():
				zip_code = raw_address[raw_address.find(state)+3:raw_address.find(state)+8]
			if len(zip_code) != 5:
				zip_code = raw_address[raw_address.find(state)+3:raw_address.find(state)+8]

			for city_name in city_list:
				if city_name in raw_address:
					city = city_name
					street_address = raw_address[:raw_address.rfind(city_name)].replace(",","").strip()
					if street_address == "301 Central Expressway South":
						zip_code = "75013"
					break
			country_code = "US"
			location_type = "<MISSING>"

		elif "Phone:" in row:
			phone = row[row.find(":")+1:row.find(":")+16].strip()
			raw_hours = rows[i+1].text.replace("Store and Car Wash:","").replace("\u200b","")
			if "," in raw_hours[-4:] or "am" in raw_hours[-4:] or raw_hours == "Store Hours: Mon-Thur 5am - 11pm":
				raw_hours = raw_hours + " " + rows[i+2].text
			hours_of_operation = raw_hours.replace("Store Hours:","").replace("\xa0", " ").replace("Directions","").strip()

		elif "Directions" in row:
			map_link = raw_row.find('a')['href']
			try:
				at_pos = map_link.rfind("@")
				latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
				longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
			except:
				latitude = "<INACCESSIBLE>"
				longitude = "<INACCESSIBLE>"

			data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
