import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('puccinissmilingteeth_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.puccinissmilingteeth.com/locations-2/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	content = base.find('div', attrs={'class': 'entry-content clearfix'})
	sections = content.findAll('p')[1:]

	data = []
	for section in sections:
		raw_data = section.find('strong').text
		city = raw_data[:raw_data.find(',')].strip()
		state = raw_data[raw_data.find(',')+1:].strip()

		items = section.findAll('a')
		index = 0
		for item in items:
			locator_domain = "puccinissmilingteeth.com"
			link = item['href']
			
			if locator_domain in link:
				phone = items[index+1].text.strip()
				req = requests.get(link, headers=headers)

				try:
					base = BeautifulSoup(req.text,"lxml")
				except (BaseException):
					logger.info('[!] Error Occured. ')
					logger.info('[?] Check whether system is Online.')
				header = base.find('div', attrs={'class': 'entry-content clearfix'})
				location_name = header.find('h4').text.strip()
				logger.info(location_name)
				street_address = header.find('p').strong.text.strip()
				if "765-746-5000" in street_address:
					street_address = street_address.replace("765-746-5000","").strip()
								
				zip_code = "<MISSING>"
				country_code = "US"
				store_number = "<MISSING>"
				location_type = location_name[location_name.find('–')+1:].strip()
				latitude = "<MISSING>"
				longitude = "<MISSING>"
				hours = header.find('small').text.replace("\n", " ").replace("\xa0", " ").strip()
				hours = re.sub(' +', ' ', hours)
				delivery = header.findAll('small')[1].text.replace("\n", " ").replace("\xa0", " ").strip()
				delivery = re.sub(' +', ' ', delivery)
				if delivery != "":
					hours_of_operation = "Hours: " + hours + " Delivery " + delivery
				else:
					hours_of_operation = "Hours: " + hours

				data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
			index = index + 1
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
