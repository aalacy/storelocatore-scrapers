from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
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
	
	base_link = "https://www.stamfordhealth.org/locations/search-results/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	all_links = []

	for i in range(5):
		req = session.get(base_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		links = base.find_all(class_="Name")
		for link in links:
			all_links.append(link)
		try:
			base_link = "https://www.stamfordhealth.org" + base.find(class_="Next")["href"]
		except:
			break
		
	data = []

	locator_domain = "stamfordhealth.org"

	for raw_link in all_links:
		link = "https://www.stamfordhealth.org/locations" + raw_link["href"].split("..")[-1]
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
		store = json.loads(script)

		final_link = store['url']
		print(final_link)
		
		location_name = store['name']
		street_address = store['address']['streetAddress']
		city = store['address']['addressLocality']
		try:
			state = store['address']['addressRegion']
		except:
			state = "<MISSING>"
		zip_code = store['address']['postalCode']
		country_code = "US"
		
		store_number = link.split("id=")[-1]
		try:
			location_type = base.find(class_="facetce9349e11bda4c59af2fe2dedcc42790").text.replace("Service Line","").strip().replace("\r\n\t\n\n",",").replace("\n",",").strip()
		except:
			location_type = "<MISSING>"
		phone = store['telephone']
		
		try:
			hours_of_operation = ""
			raw_hours = store['openingHoursSpecification']
			for hours in raw_hours:
				day = hours['dayOfWeek'].replace("http://schema.org/","")
				if len(day[0]) != 1:
					day = ' '.join(hours['dayOfWeek'])
				opens = hours['opens']
				closes = hours['closes']
				if opens != "" and closes != "":
					clean_hours = day + " " + opens + "-" + closes
					hours_of_operation = (hours_of_operation + " " + clean_hours).strip()
		except:
			hours_of_operation = "<MISSING>"
		try:
			latitude = store['geo']['latitude']
			longitude = store['geo']['longitude']
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
