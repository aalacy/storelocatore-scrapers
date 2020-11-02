import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mjmdesignershoes_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://mjmdesignershoes.com/locator/shipad_mjmshoes.html"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.findAll('td', attrs={'class': 'findastore'})

	data = []
	for item in items:
		locator_domain = "mjmdesignershoes.com"		
		raw_data = str(item).split('<br/>')
		location_name =  item.find('b').text + " " + raw_data[0][raw_data[0].rfind('>')+1:].strip()
		logger.info(location_name)
		if len(raw_data) == 5:		
			street_address = raw_data[1].replace('\n','').strip()
		elif len(raw_data) == 6:
			street_address = raw_data[1].replace('\n','').strip() + " " + raw_data[2].replace('\n','').strip()
		raw_line = item.find('a').text
		city = raw_line[:raw_line.find(',')].strip()
		state = raw_line[raw_line.find(',')+1:raw_line.rfind(' ')].strip()
		zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
		country_code = "US"
		store_number = item.find('b').text.replace(')','').strip()
		try:
			phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", item.text)[0]
		except:
			phone = "<MISSING>"
		location_type = "<MISSING>"
		map_link =item.find('a')['href']

		req = requests.get(map_link, headers=headers)

		try:
			map_base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		latitude = map_base.find('meta', attrs={'property': 'place:location:latitude'})['content']
		longitude = map_base.find('meta', attrs={'property': 'place:location:longitude'})['content']
		hours_of_operation = hours_of_operation = base.find('div', attrs={'class': 'bodycopy'}).text
		hours_of_operation = hours_of_operation[hours_of_operation.find('open')+5:]

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
