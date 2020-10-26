import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mydannys_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://dannysrestaurants.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.findAll('div', attrs={'class': 'location-item'})

	data = []
	for item in items:
		locator_domain = "dannysrestaurants.com"
		location_name = base.title.text.strip()
		location_name = location_name[location_name.find("–")+1:].strip()
		street_address = item.find('a')['title']
		city = "Laredo"
		state = "TX"
		zip_code = "<MISSING>"
		country_code = "US"
		store_number = "<MISSING>"
		phone =  item.find('a').text.strip()
		location_type = "<MISSING>"

		link = item.find('iframe')['src']
		start_point = link.find("2d") + 2
		longitude = link[start_point:link.find('!',start_point)]
		long_start = link.find('!',start_point)+3
		latitude = link[long_start:link.find('!',long_start)]
		try:
			int(latitude[4:8])
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		hours_of_operation = "<MISSING>"

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
