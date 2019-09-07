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
	
	base_link = "http://kellystavern.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	main_page = base.findAll('div', attrs={'class': 'popup_anchor'})
	items = set()
	for item in main_page:
		try:
			link = "http://kellystavern.com/" + item.a['href']
			items.add(link)
		except:
			continue

	data = []
	for link in items:
		print ("Getting link: " + link)
		req = requests.get(link, headers=headers)

		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')

		locator_domain = "kellystavern.com"
		content = base.findAll('div', attrs={'class': 'clearfix grpelem'})[-1]
		location_name = content.findAll('p')[0].text.strip()
		street_address = content.findAll('p')[1].text.strip()
		phone = content.findAll('p')[3].text.strip()
		raw_data = content.findAll('p')[2].text.strip()
		hours_of_operation = (content.findAll('p')[6].text.strip() + " " + content.findAll('p')[7].text.strip()).replace(',','')
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)
		if "Suite" in raw_data:
			street_address = street_address + " " + raw_data
			raw_data = content.findAll('p')[3].text.strip()
			phone = content.findAll('p')[4].text.strip()
			hours_of_operation = (content.findAll('p')[7].text.strip() + " " + content.findAll('p')[8].text.strip()).replace(',','')
			hours_of_operation = re.sub(' +', ' ', hours_of_operation)
		city = raw_data[:raw_data.find(',')].strip()
		state = raw_data[raw_data.find(',')+1:raw_data.rfind(' ')].strip()
		zip_code = raw_data[raw_data.rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"		
		location_type = location_name[:location_name.rfind(',')].strip()
		latitude = "<MISSING>"
		longitude = "<MISSING>"
		
		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()