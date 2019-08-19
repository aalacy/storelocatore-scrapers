import requests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "website"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.thriftway.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	table = base.find('table')
	items = table.findAll("tr")
	items.pop(0)

	data = []
	for item in items:
		locator_domain = "thriftway.com"		
		location_name = item.find('td').text.split('\n')[2].strip()
		print (location_name)
		street_address = item.findAll('td')[1].text.strip()
		city = item.find('strong').text.strip()
		state = "<MISSING>"
		zip_code = "<MISSING>"
		country_code = "US"
		store_number = "<MISSING>"
		phone = item.findAll('td')[2].text.strip()
		location_type = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"
		hours_of_operation = "<MISSING>"
		website = item.find('a')['href']
		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, website])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
