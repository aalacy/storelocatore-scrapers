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
	
	base_link = "https://www.localiyours.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	content = base.find('div', attrs={'class': 'pm-map-wrap pm-location-search-list'})
	items = content.findAll('div', attrs={'class': 'col-xs-12'})

	data = []
	for item in items:
		locator_domain = "localiyours.com"
		raw_data = str(item.find('p')).replace("<p>","").split('<br/>')
		raw_data.pop(-1)
		raw_data.pop(-1)

		location_name = raw_data[0]
		
		if len(raw_data) == 3:
			street_address = raw_data[1][raw_data[1].find("span>")+5:raw_data[1].rfind("<!")]
		else:
			street_address = raw_data[1].replace("<!-- -->","").replace("\xa0", " ")
			street_address = street_address[street_address.find("span>")+5:]
			street_address = street_address + " " + raw_data[2][raw_data[2].find("<span>")+6:raw_data[2].rfind("<!")]
		
		city = raw_data[-1][:raw_data[-1].find(',')].strip()
		state = raw_data[-1][raw_data[-1].find(',')+1:raw_data[-1].rfind(' ')].strip()
		zip_code = raw_data[-1].replace("</a>","")[raw_data[-1].rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone =  item.findAll('p')[1].text.strip()
		location_type = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"
		hours_of_operation = item.find('div', attrs={'class': 'hours-times'}).text
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()