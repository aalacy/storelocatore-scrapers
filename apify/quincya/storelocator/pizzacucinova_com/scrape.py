from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pizzacucinova_com')




def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://pizzacucinova.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	session = SgRequests()

	req = session.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.findAll('div', attrs={'class': 'inner-content'})

	data = []
	for item in items:
		link = item.find('a')['href']

		req = session.get(link, headers=headers)
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		locator_domain = "pizzacucinova.com"		
		location_name = base.find('h2').text.strip()
		logger.info(location_name)
		
		raw_data = str(base.find('p', attrs={'class': 'address'})).replace('<p>',"").replace('</p>',"").replace('\n',"").split('<br/>')
		street_address = raw_data[0][raw_data[0].rfind(">")+1:].strip()
		raw_line = raw_data[1]
		city = raw_line[:raw_line.rfind(',')].strip()
		state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
		zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", str(base.text))[0]
		location_type = "<MISSING>"
		hours_of_operation = base.find('div', attrs={'class': 'normal-hours'}).get_text(separator=u' ').replace("\n"," ").replace("Normal business hours","").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)
		
		try:
			new_base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		raw_gps = str(new_base)
		start_point = raw_gps.find("latitude") + 10
		latitude = raw_gps[start_point:raw_gps.find(",",start_point)].strip()
		semi_point = raw_gps.find("longitude",start_point)
		longitude = raw_gps[semi_point+12:raw_gps.find('}',semi_point)].strip()

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
