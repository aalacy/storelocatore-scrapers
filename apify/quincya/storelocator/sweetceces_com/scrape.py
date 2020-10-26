import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sweetceces_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://www.sweetceces.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	content = base.find('div', attrs={'id': 'main-content'})
	items = content.findAll("li")

	base.findAll('div', attrs={'class': 'container'})[2]

	data = []
	for item in items:
		if "Coming Soon" in item.text:
			continue
		else:
			location_type = "<MISSING>"
		link = item.a['href']

		req = requests.get(link, headers=headers)

		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		content = base.find('div', attrs={'id': 'main-content'})
		locator_domain = "sweetceces.com"
		
		raw_data = str(content.find('p')).replace('</p>',"").replace('\n',"").split('<br/>')
		location_name = raw_data[0][raw_data[0].rfind('>')+1:].strip()
		if location_name != "":
			street_address = raw_data[1].replace(',',"").strip()
			city = raw_data[2][:raw_data[2].find(',')].strip()
			state = raw_data[2][raw_data[2].find(',')+1:raw_data[2].rfind(' ')].strip()
			zip_code = raw_data[2][raw_data[2].rfind(' ')+1:].strip()
		else:
			location_name = raw_data[1].strip()
			street_address = raw_data[2].strip()
			city = raw_data[3][:raw_data[3].find(',')].strip()
			state = raw_data[3][raw_data[3].find(',')+1:raw_data[3].rfind(' ')].strip()
			zip_code = raw_data[3][raw_data[3].rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", str(content.find('p')))[0]
		except:
			if "Cool Springs" in location_name:
				phone = raw_data[-1][raw_data[-1].find(" ")+1:raw_data[-1].find("<")]
				phone = phone + raw_data[-1][raw_data[-1].find('">')+2:raw_data[-1].find('">')+6]
			else:
				phone = "<MISSING>"	

		link = base.findAll('iframe')[1]['src']
		start_point = link.find("2d") + 2
		longitude = link[start_point:link.find('!',start_point)]
		long_start = link.find('!',start_point)+3
		latitude = link[long_start:link.find('!',long_start)]

		hours_of_operation = "<MISSING>"

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
