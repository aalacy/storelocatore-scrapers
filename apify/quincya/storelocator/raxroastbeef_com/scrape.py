import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('raxroastbeef_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://raxroastbeef.com/locations.html"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.findAll('div', attrs={'class': 'clearfix grpelem'})
	items = items[:-1]
	data = []
	for item in items:
		locator_domain = "raxroastbeef.com"
		location_name = item.findAll('p')[0].text.strip()		
		if "Coming" in location_name:
			continue
		logger.info(location_name)
		street_address = item.findAll('p')[1].text.strip()
		raw_line = item.findAll('p')[2].text.strip()
		city = raw_line[:raw_line.find(",")].strip()
		state = raw_line[raw_line.find(',')+1:raw_line.rfind(' ')].strip()
		zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
		store_number = "<MISSING>"
		try:
			phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", item.text)[0]
		except:
			phone = "<MISSING>"
		country_code = "US"
		location_type = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"
		try:
			hours_of_operation = item.findAll('p')[7].text.strip()
		except:
			pass

		try:
			hours_of_operation = hours_of_operation + " " + item.findAll('p')[8].text.strip()
		except:
			pass

		try:
			hours_of_operation = hours_of_operation + " " + item.findAll('p')[9].text.strip()
		except:
			pass		

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
