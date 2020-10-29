import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('graulsmarket_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "email"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.graulsmarket.com/locations.html"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.findAll('td', attrs={'class': 'wsite-multicol-col'})
	
	data = []
	for item in items:
		locator_domain = "graulsmarket.com"
		try:
			location_name = item.find('h2').text.replace('​',"").strip()
			logger.info(location_name)
		except:
			continue
		raw_data = str(item.div).replace('<div>',"").replace('</div>',"").replace('\n',"").replace('​',"").strip().split('<br/>')
		street_address = raw_data[0][raw_data[0].rfind('>')+1:].strip()
		city = raw_data[1][:raw_data[1].find(',')].strip()
		state = raw_data[1][raw_data[1].rfind(',')+1:raw_data[1].rfind(' ')].strip()
		zip_code = raw_data[1][raw_data[1].rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", str(item))[0]
		except:
			phone = "<MISSING>"
		location_type = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"
		hours_of_operation = raw_data[3] + " " + raw_data[4]
		try:
			email = raw_data[9][raw_data[9].rfind('">')+2:raw_data[9].rfind("<")].strip()
			if email == "":
				email = "<MISSING>"
		except:
			email = "<MISSING>"
		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, email])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
