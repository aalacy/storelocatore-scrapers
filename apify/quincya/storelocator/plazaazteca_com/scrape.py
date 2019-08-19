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
	
	base_link = "https://www.plazaazteca.com/locations-hours"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	headings = base.findAll('h3', attrs={'class': 'header-4'})
	details = base.findAll('div', attrs={'class': 'row location'})
	
	data = []
	for index in range(0,len(headings)):

		locator_domain = "plazaazteca.com"
		location_name = headings[index].text.strip()
		if "*" in location_name:			
			location_type = location_name[location_name.find("*")+1:-1].strip()
			location_name = location_name[:location_name.find("*")].strip()
		else:
			location_type = "<MISSING>"
		print (location_name)

		raw_data = str(details[index].find('div', attrs={'class': 'col-xs-6 address-info'}).p).replace('<p>',"").replace('</p>',"").replace('\n',"").split('<br/>')
		street_address = raw_data[0].strip()
		raw_line = raw_data[1].strip()
		city = raw_line[:raw_line.rfind(',')].strip()
		state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
		zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = raw_data[2].strip()
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		hours_of_operation = details[index].find('div', attrs={'class': 'col-xs-6 hours-info'}).get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)
		if hours_of_operation == "":
			hours_of_operation = "<MISSING>"

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
