import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('taylorstpizza_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://taylorstpizza.com/?page_id=317"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	content = base.find('div', attrs={'class': 'et_pb_row et_pb_row_0'})
	
	
	data = []
	locator_domain = "taylorstpizza.com"
	location_name = base.title.text.strip()
	logger.info(location_name)
	raw_data = content.findAll('h3')[1].text
	street_address = raw_data[:raw_data.find("|")].strip()
	city = location_name[:location_name.find(" ")]
	state = "<MISSING>"
	zip_code = "<MISSING>"
	country_code = "US"
	store_number = "<MISSING>"
	try:
		phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", raw_data)[0]
	except:
		phone = "<MISSING>"
	location_type = "<MISSING>"
	latitude = "<MISSING>"
	longitude = "<MISSING>"
	hours_of_operation = "<MISSING>"

	data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
