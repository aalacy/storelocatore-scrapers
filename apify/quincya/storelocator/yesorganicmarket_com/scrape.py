import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('yesorganicmarket_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "raw_address", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://www.yesorganicmarket.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	content = base.find('div', attrs={'class': 'col sqs-col-3 span-3'})
	items = content.findAll('p')

	data = []
	hours_of_operation = items[-3].text 
	for item in items:
		locator_domain = "yesorganicmarket.com"

		raw_data = item.text
		location_name = raw_data[:raw_data.find(":")].strip()
		if location_name != "":
			if "Everyday" not in location_name:
				logger.info(location_name)
				raw_address = raw_data[raw_data.find(":")+1:raw_data.rfind(" ")].strip()
				if ("(") in raw_address:
					raw_address = raw_address[:raw_address.find("(")]
				street_address = "<INACCESSIBLE>"
				city = "<INACCESSIBLE>"
				state = "<INACCESSIBLE>"
				zip_code = "<MISSING>"
				country_code = "US"
				store_number = "<MISSING>"
				try:
					phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", raw_data)[0]
				except:
					try:
						phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", raw_data)[0]
					except:
						phone = "<MISSING>"
				location_type = "<MISSING>"
				latitude = "<MISSING>"
				longitude = "<MISSING>"

				data.append([locator_domain, location_name, raw_address, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
