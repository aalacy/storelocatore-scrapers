import requests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "raw_address", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "http://j-bees.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	data = []
	raw_sect = str(base.findAll('script', attrs={'type': 'text/javascript'})[1]).replace('["<strong>Address: </strong>',"")
	section = raw_sect[raw_sect.find('[')+1:raw_sect.find("];")].strip().split('\r\n')
	for item in section:
		item = re.sub(' +', ' ', item).strip()
		item = item[:-5]
		if "London" in item:
			continue

		locator_domain = "j-bees.com"
		location_name = base.title.text.strip()
		raw_address = item[:item.find(',')]
		street_address = "<INACCESSIBLE>"
		city = "<INACCESSIBLE>"
		state = item[item.find(',')+1:item.find(',')+4].strip()
		zip_code = item[item.find(',')+4:item.find('<')].strip()
		if len(zip_code) > 12:
			raw_data = item[:item.find('<')]
			raw_address = raw_data[:raw_data.rfind(',')]
			state = raw_data[raw_data.rfind(',')+1:raw_data.rfind(',')+4].strip()
			zip_code = raw_data[raw_data.rfind(' ')+1:]
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", item)[0]
		except:
			phone = re.findall("[[\d]{3}-[\d]{3} -[\d]{4}", item)[0]
		location_type = "<MISSING>"
		latitude = item[item.rfind('",')+2:item.rfind(',')].strip()
		longitude = item[item.rfind(',')+1:].strip()
		hours_of_operation = "<MISSING>"

		data.append([locator_domain, location_name, raw_address, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
