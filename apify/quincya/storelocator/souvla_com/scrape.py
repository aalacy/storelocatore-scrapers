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
	
	base_link = "https://www.souvla.com/locations/"

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

	data = []

	script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
	store_data = json.loads(script)['subOrganization']

	for store in store_data:

		locator_domain = "souvla.com"
		location_name = store['name']
		print(location_name)

		street_address = store['address']['streetAddress']
		city = store['address']['addressLocality']
		state = store['address']['addressRegion']
		zip_code = store['address']['postalCode']

		country_code = "US"
		store_number = "<MISSING>"
		
		location_type = "<MISSING>"
		phone = store['telephone']
		if not phone:
			phone = "<MISSING>"

		raw_hours = store['description'].replace("&ndash;","-").replace("Hours","").replace("&amp;","&").replace("PM","PM ").replace("day","day ").replace("Order Online","").strip()
		hours_of_operation = (re.sub(' +', ' ', raw_hours)).strip()

		link = store['url']

		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		latitude = base.find(class_="gmaps")['data-gmaps-lat']
		longitude = base.find(class_="gmaps")['data-gmaps-lng']

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
