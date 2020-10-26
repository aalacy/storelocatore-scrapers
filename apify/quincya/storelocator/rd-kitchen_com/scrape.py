from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rd-kitchen_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://rd-kitchen.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}
	session = SgRequests()
	req = session.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.find('div', attrs={'id': 'locations'}).ul
	items = items.findAll('li')
	data = []
	for item in items:
		link = "https://rd-kitchen.com" + item.a['href']

		req = session.get(link, headers=headers)

		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')
	
		locator_domain = "rd-kitchen.com"
		location_name = base.find('h3').text.replace("Kitchen","Kitchen ").strip()
		street_address = base.find('span', attrs={'itemprop': 'streetAddress'}).text
		city = base.find('span', attrs={'itemprop': 'addressLocality'}).text
		state = base.find('span', attrs={'itemprop': 'addressRegion'}).text
		zip_code = base.find('span', attrs={'itemprop': 'postalCode'}).text
		country_code = "US"
		store_number = "<MISSING>"
		phone = base.find('a', attrs={'class': 'phone'}).text
		menu_item = base.find('div', attrs={'class': 'contact'})
		location_type = "<MISSING>"
		hours_of_operation = base.find('div', attrs={'class': 'hours'}).get_text(separator=u' ').replace("\n"," ").replace("  "," ").replace("–","-").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		map_link = base.find(class_="address").a["href"]
		req = session.get(map_link, headers = headers)
		try:
			maps = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		try:
			raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
			longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
