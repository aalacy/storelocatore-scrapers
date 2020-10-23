import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jalexandersholdings_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://jalexandersholdings.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')
	
	data = []

	items = base.findAll('div', attrs={'class': 'restaurantCard'})
	locator_domain = "jalexandersholdings.com"
	for item in items:
		location_name = item.find('h4').text.strip()
		location_name = location_name[:location_name.find('|')].strip()
		
		if "Coming" not in location_name:
			logger.info(location_name)
			raw_data = str(item.find('address')).replace('<p>',"").replace('</p>',"").replace('\n',"").replace('\t'," ").strip().split('<br/>')
			street_address = raw_data[0][raw_data[0].find('>')+1:].strip()
			raw_line = raw_data[1]
			if "Suite" in raw_line:
				street_address = (street_address + " " + raw_line).strip()
				raw_line = raw_data[2]
			city = raw_line[:raw_line.rfind(',')].strip()
			state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
			zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
			try:
				int(zip_code)
			except:
				raw_data = str(item.find('address')).replace('<p>',"").replace('</p>',"").replace('\n',"").replace('\t'," ").strip().split('<br/>')
				street_address = raw_data[0][raw_data[0].find('>')+1:].strip()
				street_address = (street_address + raw_data[1].strip()).strip()
				raw_line = raw_data[2]
				city = raw_line[:raw_line.rfind(',')].strip()
				state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
				zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
			country_code = "US"
			store_number = "<MISSING>"
			try:
				phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", item.text)[0]
			except:
				phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", item.text)[0]
			location_type = "<MISSING>"
			latitude = "<MISSING>"
			longitude = "<MISSING>"
			hours_of_operation = item.find('div', attrs={'class': 'hours'}).p.get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
			hours_of_operation = re.sub(' +', ' ', hours_of_operation)

			data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
