from bs4 import BeautifulSoup
import csv
import time
import re

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('altabank_com')




def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	session = SgRequests()

	url = "https://altabank.com/locations/"

	HEADERS = { "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36" }

	req = session.get(url, headers = HEADERS)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	locations = base.findAll(class_='location-card')
	locator_domain = "altabank.com"

	data = []
	for location in locations:

		location_name = location.find(class_="branch-name").h5.text

		raw_address = location.find(class_="branch-address").find_all('p')
		street_address = raw_address[0].text
		city_line = raw_address[1].text
		city = city_line[:city_line.find(',')].strip()
		state = city_line[city_line.find(',')+1:city_line.rfind(' ')].strip()
		zip_code = city_line[city_line.rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = location.find(class_="branch-numbers").p.text.replace('Phone: ','')
		location_type = "<MISSING>"
		hours_of_operation = location.find(class_='branch-hours').get_text(separator=u' ').replace("\n"," ").replace("\xa0","").replace("Hours of Operation:","").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		raw_gps = location.find('a')['href']
		start_point = raw_gps.find("@")
		latitude = raw_gps[start_point+1:raw_gps.find(',',start_point)]
		long_start = raw_gps.find(',',start_point)+1
		longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
		
		try:
			int(latitude[4:8])
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()