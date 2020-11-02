import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('badmaashla_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.badmaashla.com/welcome"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	section = base.find('div', attrs={'class': 'footer-inner'})
	items = section.findAll('div', attrs={'class': 'col sqs-col-6 span-6'})[0:2]
	
	data = []
	for item in items:
		locator_domain = "badmaashla.com"		
		location_name = item.find('strong').text.strip()
		logger.info(location_name)
		
		raw_data = str(item.find('p')).replace('<p>',"").replace('</p>',"").replace('\n',"").replace('\xa0',"").split('<br/>')
		street_address = raw_data[1][:raw_data[1].find(",")].strip()
		city = raw_data[1][raw_data[1].find(",")+1:].strip()
		state = "<MISSING>"
		zip_code = "<MISSING>"
		country_code = "US"
		store_number = "<MISSING>"
		phone = item.findAll('strong')[1].text.strip()
		location_type = "<MISSING>"

		raw_gps = item.find('div', attrs={'class': 'sqs-block map-block sqs-block-map'})['data-block-json']

		start_point = raw_gps.find("mapLat") + 8
		latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
		long_start = raw_gps.find(':',start_point)+1
		longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
		try:
			int(latitude[4:8])
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"
			
		hours_of_operation = item.findAll('div', attrs={'class': 'sqs-block-content'})[2].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
