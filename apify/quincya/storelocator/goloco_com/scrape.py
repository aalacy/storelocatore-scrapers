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
	
	base_link = "http://goloco.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	items = base.findAll('div', attrs={'class': 'col-md-3 info locations-padding'})

	data = []
	for item in items:
		locator_domain = "goloco.com"
		location_type = item.find('h3').text.strip()
		print (location_type)
		
		raw_data = str(item.find('address')).replace('</p>',"").replace("\t","").split('<br/>')
		street_address = raw_data[0][raw_data[0].rfind('>')+1:].strip()
		raw_data[1] = raw_data[1].strip()
		city = raw_data[1][:raw_data[1].find(',')].strip()
		state = raw_data[1][raw_data[1].find(',')+1:raw_data[1].rfind(' ')].strip()
		zip_code = raw_data[1][raw_data[1].rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", raw_data[2])[0]
		except:
			phone = "<MISSING>"

		link = 'http://goloco.com' + item.find('a')['href']

		req = requests.get(link, headers=headers)

		try:
			new_base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')
		
		raw_name = new_base.find('div', attrs={'class': 'side vertical-divider-left'})
		raw_name = str(raw_name.findAll('li')[1]).replace('</p>',"").replace("\t","").split('<br/>')
		location_name = raw_name[0][raw_name[0].rfind('>')+1:].strip() + " " + location_type
		try:
			hours_of_operation = new_base.find('div', attrs={'class': 'main col-md-8'}).strong.text
		except:
			hours_of_operation = "<MISSING>"
		if "Open" not in hours_of_operation:
			hours_of_operation = "<MISSING>"

		link = new_base.find('iframe')['src']
		start_point = link.find("2d") + 2
		longitude = link[start_point:link.find('!',start_point)]
		long_start = link.find('!',start_point)+3
		latitude = link[long_start:link.find('!',long_start)]
		
		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
