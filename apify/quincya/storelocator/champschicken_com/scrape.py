from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

from sgselenium import SgSelenium

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	driver = SgSelenium().chrome()
	time.sleep(2)

	states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
				"HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
				"MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
				"NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
				"SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

	data = []
	found_poi = []
	for state in states:
		print("Search: " + state)
		driver.get("https://champschicken.com/locate/?loc=" + state)
		time.sleep(randint(2,4))

		base = BeautifulSoup(driver.page_source,"lxml")

		items = base.find_all(class_="result")
		print("Found %s POI" %len(items))
		if not items:
			continue

		locator_domain = "champschicken.com"

		for item in items:
			location_name = str(item.h3)[4:].split("<span")[0].strip()
			link = item.a['href']
			if link in found_poi:
				continue
			found_poi.append(link)
			print(link)

			raw_address = str(item.p).replace("\xa0"," ").replace("<p>","").replace("</p>","").split("<br/>")
			street_address = raw_address[0].replace(" , Attn: Cadillac Food Service - Cafeteria","").strip()
			city = raw_address[1].split(",")[0].strip()
			state = raw_address[1].split(",")[1].strip().split()[0]
			zip_code = raw_address[1].split(",")[1].strip().split()[1]
			country_code = "US"
			store_number = "<MISSING>"
			location_type = "<MISSING>"
			try:
				phone = re.findall(r'\([0-9]{3}\) [0-9]{3}-[0-9]{4}', item.text)[0]
			except:
				try:
					phone = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', item.text)[0]
				except:
					phone = "<MISSING>"
			hours_of_operation = "<MISSING>"

			latitude = "<MISSING>"
			longitude = "<MISSING>"

			req = session.get(link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")
			all_scripts = base.find_all('script')
			for script in all_scripts:
				if "lat=" in str(script):
					script = str(script)
					lat_pos = script.find('lat=') + 4
					latitude = script[lat_pos:script.find('&',lat_pos)]
					long_pos = script.find('lon=') + 4
					longitude = script[long_pos:script.find('&',long_pos)]
					break
				
			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
