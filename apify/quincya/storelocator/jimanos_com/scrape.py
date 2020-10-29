import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jimanos_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.jimanos.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.findAll('a', attrs={'class': 'location-button'})
	
	data = []
	for item in items:
		link = item['href']

		req = requests.get(link, headers=headers)
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		locator_domain = "jimanos.com"		
		location_name = base.find('h1').text.strip()
		logger.info(location_name)
		
		raw_data = str(base.find('span', attrs={'itemprop': 'address'})).replace('<p>',"").replace('</p>',"").replace('\n',"").replace(',',"").split('<br/>')
		street_address = raw_data[0][raw_data[0].rfind(">")+1:].strip()
		raw_line = base.find('span', attrs={'itemprop': 'addressLocality'}).text.strip()
		city = raw_line[:raw_line.rfind(',')].strip()
		state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
		zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = base.find('span', attrs={'itemprop': 'telephone'}).text.strip()
		location_type = "<MISSING>"

		raw_gps = base.find('a', attrs={'id': 'directions'})['href']

		start_point = raw_gps.find("@") + 1
		latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
		long_start = raw_gps.find(',',start_point)+1
		longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
		try:
			int(latitude[4:8])
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		hours_of_operation = base.find('table', attrs={'class': 'location-table'}).get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
