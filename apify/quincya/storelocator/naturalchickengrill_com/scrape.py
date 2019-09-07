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
	
	base_link = "https://www.naturalchickengrill.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	items = base.findAll('div', attrs={'class': 'c-location-list__content'})

	data = []
	for item in items:
		locator_domain = "naturalchickengrill.com"
		location_name = item.find('a').text.strip()
		
		raw_data = str(item.find('p', attrs={'class': 'c-location-list__info'})).replace('<p>',"").replace('</p>',"").split('<br/>')
		street_address = raw_data[0][raw_data[0].rfind('\t'):].strip()
		raw_data[1] = raw_data[1].strip()
		city = raw_data[1][:raw_data[1].find(' ')].strip()
		state = raw_data[1][raw_data[1].find(' ')+1:raw_data[1].rfind(' ')].strip()
		zip_code = raw_data[1][raw_data[1].rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = re.findall("[[\d]{3} [\d]{3} [\d]{4}", raw_data[2])[0]
		except:
			phone = "<MISSING>"
		location_type = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"
		hours_of_operation = item.findAll('div', attrs={'class': 'c-location-list__block'})[1]
		hours_of_operation = hours_of_operation.findAll('span', attrs={'class': 's1'})
		hours_list = []
		for hours in hours_of_operation:
			hours_list.append((hours.text.replace("\n", " ").replace("\xa0", " ")))
		hours_of_operation = ', '.join(hours_list)
		hours_of_operation = hours_of_operation.replace(",","")

		if hours_of_operation == "":
			hours_of_operation = item.findAll('div', attrs={'class': 'c-location-list__block'})[1]
			hours_of_operation = hours_of_operation.findAll('p')[2].text.replace("\n", " ").replace("\xa0", " ")
			hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
