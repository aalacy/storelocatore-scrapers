from sgrequests import SgRequests
import requests
from bs4 import BeautifulSoup
import csv
from random import randint
import time
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "store_manager"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "http://holidayfoodsonline.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	session = SgRequests()

	req = session.get(base_link, headers=headers)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	items = base.find_all('div', attrs={'data-tab-icon': 'fa fa-shopping-cart'})
	
	data = []
	for item in items:
		locator_domain = "holidayfoodsonline.com"
		location_name = item.find('h2').text.strip()
		print (location_name)
		
		raw_data = item.ul.find_all('li')
		raw_address = raw_data[3].text.strip()
		city = location_name[:location_name.find(',')].strip()
		street_address = raw_address[:raw_address.find(city)].replace("Address:","").strip()[:-1]
		state = location_name[location_name.find(',')+1:].strip()
		zip_code = raw_address[-6:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = raw_data[2].text.replace("Phone:","").strip()
		location_type = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"
		hours_of_operation = raw_data[0].text.replace("Hours:","").strip()
		store_manager = raw_data[1].text.replace("Store Manager:", "").strip()
		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, store_manager])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
