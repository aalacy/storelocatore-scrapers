import requests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.thefuzzypeach.com/find-a-location"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	items = base.findAll('tr')
	items.pop(0)

	data = []
	for item in items:
		locator_domain = "thefuzzypeach.com"
		location_name = "<MISSING>"
		street_address = item.find('span', attrs={'itemprop': 'streetAddress'}).text
		city = item.find('span', attrs={'itemprop': 'addressLocality'}).text
		state = item.find('span', attrs={'itemprop': 'addressRegion'}).text
		zip_code = item.find('span', attrs={'itemprop': 'postalCode'}).text
		country_code = "US"
		store_number = "<MISSING>"
		offer = []
		phone = item.find('td', attrs={'class': 'views-field views-field-field-phone'}).a.text.strip()
		if len(str(item.find('td', attrs={'class': 'views-field views-field-field-catering'}))) > 80:
			offer.append("Catering")
		if len(str(item.find('td', attrs={'class': 'views-field views-field-field-fundraising'}))) > 80:
			offer.append("Fundraising")
		location_type = ', '.join(offer)
		latitude = item.find('div', attrs={'class': 'hidden'}).get('data-lat') 
		longitude = item.find('div', attrs={'class': 'hidden'}).get('data-long')
		hours_of_operation = "<MISSING>"

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()