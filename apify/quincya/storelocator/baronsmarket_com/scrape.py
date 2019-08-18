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
	
	base_link = "http://baronsmarket.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	items = base.findAll('div', attrs={'class': 'accordion_title'})

	data = []
	for item in items:
		if "Opening" not in item.text:
			locator_domain = "baronsmarket.com"
			location_name = item.find('h2').text.strip()
			
			raw_data = str(item.find('a').text).replace("  ",";")
			street_address = raw_data[:raw_data.rfind(';')].strip()
			city = raw_data[raw_data.rfind(';')+1:raw_data.find(',')].strip()
			state = raw_data[raw_data.find(',')+1:raw_data.rfind(' ')].strip()
			zip_code = raw_data[raw_data.rfind(' ')+1:].strip()
			country_code = "US"
			store_number = "<MISSING>"
			try:
				phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", item.text)[0]
			except:
				phone = "<MISSING>"
			location_type = "<MISSING>"
			latitude = "<MISSING>"
			longitude = "<MISSING>"
			hours_of_operation = str(item.findAll('div', attrs={'class': 'accordion_col'})[1]).replace("</div>", "").split('<br/>')
			hours_of_operation = hours_of_operation[-1].strip()

			data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
