import requests
from bs4 import BeautifulSoup
import csv

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://he-equipment.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print '[!] Error Occured. '
		print '[?] Check whether system is Online.'

	rows = base.findAll('h5')

	data = []
	for row in rows:
		link = row.find('a')['href']

		req = requests.get(link, headers=headers)

		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print '[!] Error Occured. '
			print '[?] Check whether system is Online.'

		locator_domain = "he-equipment.com"
		
		raw_data = base.find('div', attrs={'class': 'medium-3 columns locationInformation sidebarList'}).p.encode('utf-8').strip().replace('<p>',"").replace('&amp;',"&").replace("\n","").split('<br/>')
		location_name = base.find('h1').text.strip()
		street_address = raw_data[1]
		last_line = raw_data[2]
		city = last_line[:last_line.find(',')].strip()
		state = last_line[last_line.find(',')+1:last_line.rfind(' ')].strip()
		zip_code = last_line[last_line.rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = base.find('a', attrs={'class': 'tel'}).text.encode('utf-8').strip()
		header = base.find('section', attrs={'class': 'row pageTitle'})
		try:
			location_type = header.find('h3').text.strip()
		except:
			location_type = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"
		hours = base.find('div', attrs={'class': 'medium-3 columns locationInformation sidebarList'})
		hours_of_operation = hours.findAll('p')[2].get_text(separator=u' ').encode('utf-8').strip()

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
		print "Got page details"

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()