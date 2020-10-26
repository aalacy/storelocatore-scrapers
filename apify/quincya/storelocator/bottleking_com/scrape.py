import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bottleking_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "email"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://bottleking.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.findAll('div', attrs={'class': 'over_store_div'})

	data = []
	for item in items:
		locator_domain = "bottleking.com"
		location_name = item.find('a').get_text(separator=u' ').replace("\n"," ").replace("\r"," ").strip()
		location_name = re.sub(' +', ' ', location_name)
		if location_name != "":
			logger.info(location_name)
			street_address = item.find('div', attrs={'class': 'store_address'}).text.replace("\n"," ").replace("\r"," ").strip()
			raw_data = item.find('div', attrs={'class': 'store_citystatezip'}).text.replace("\n"," ").replace("\r"," ").strip()
			city = raw_data[:raw_data.find(',')].strip()
			state = raw_data[raw_data.find(',')+1:raw_data.rfind(' ')].strip()
			zip_code = raw_data[raw_data.rfind(' ')+1:].strip()
			country_code = "US"
			store_number = "<MISSING>"
			phone =  item.find('div', attrs={'class': 'store_phone'}).text.replace("\n"," ").replace("\r"," ").strip()
			location_type = "<MISSING>"
			latitude = "<MISSING>"
			longitude = "<MISSING>"
			hours_of_operation =  "<MISSING>"
			email = item.find('div', attrs={'class': 'store_email'}).text.replace("\n"," ").replace("\r"," ").strip()

			data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, email])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
