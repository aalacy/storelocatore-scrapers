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
	
	base_link = "https://www.wichcraft.com/locations-hours/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')
	
	items = base.findAll('a', attrs={'class': 'card__btn'})
	
	data = []
	for item in items:
		link = "https://www.wichcraft.com" + item['href']

		req = requests.get(link, headers=headers)
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')

		locator_domain = "wichcraft.com"		
		location_name = base.find('h2').text.strip()
		print (location_name)
		
		raw_data = str(base.find('a', attrs={'data-bb-track-category': 'Address'}).text).replace('<p>',"").replace('\t',"").replace('\n',"")
		street_address = raw_data[:raw_data.find(',')].strip()
		city = raw_data[raw_data.find(',')+1:raw_data.rfind(',')].strip()
		state = raw_data[raw_data.rfind(',')+1:raw_data.rfind(',')+4].strip()
		zip_code = raw_data[raw_data.rfind(' ')+1:].strip()
		try:
			int(zip_code)
		except:
			zip_code = "<MISSING>"
		country_code = "US"
		store_number = "<MISSING>"
		phone = re.findall("[[\d]{3}.[\d]{3}.[\d]{4}", base.text)[0]
		location_type = "<MISSING>"
		maps = base.find('div', attrs={'class': 'gmaps'})
		latitude = maps['data-gmaps-lat']
		longitude = maps['data-gmaps-lng']
		try:
			int(latitude[4:8])
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		hours_of_operation = base.findAll('div', attrs={'class': 'col-md-6'})[1].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
