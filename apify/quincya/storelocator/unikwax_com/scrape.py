import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('unikwax_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://unikwax.com/studio-locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')
	
	sections = base.findAll('div', attrs={'class': 'card'})
	data = []

	for section in sections:
		if "Coming Soon" not in section.text:
			state = section.find('a').text.strip()
			items = section.findAll('li')

			for item in items:
				locator_domain = "unikwax.com"		
				location_name = item.find('span', attrs={'class': 'location__title'}).text.strip()
				logger.info(location_name)				
				city = "<MISSING>"
				zip_code = "<MISSING>"
				country_code = "US"
				store_number = "<MISSING>"
				phone = item.find('a', attrs={'class': 'location__phone--number hidden-md-down'}).text.strip()
				location_type = "<MISSING>"

				link = item.find('a')['href']
				req = requests.get(link, headers=headers)
				try:
					new_base = BeautifulSoup(req.text,"lxml")
				except (BaseException):
					logger.info('[!] Error Occured. ')
					logger.info('[?] Check whether system is Online.')
				street_address = new_base.find('p', attrs={'class': 'address'}).text.strip()
				raw_gps = str(new_base)
				start_point = raw_gps.find('lat":')+5
				latitude = raw_gps[start_point:raw_gps.find(",",start_point)].replace('"','').strip()
				semi_point = raw_gps.find("lng",start_point)
				longitude = raw_gps[semi_point+5:raw_gps.find('}',semi_point)].replace('"','').strip()
				hours_of_operation = new_base.findAll('div', attrs={'class': 'col-sm-6'})[1].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").replace("Studio Hours", "").strip()
				hours_of_operation = re.sub(' +', ' ', hours_of_operation)
				data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
