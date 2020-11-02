import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hotnjuicycrawfish_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "raw_address", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://hotnjuicycrawfish.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.findAll('div', attrs={'class': 'iconbox-wrapper w-col w-col-3 w-col-medium-6'})

	data = []
	for item in items:
		locator_domain = "hotnjuicycrawfish.com"
		try:
			page_link = "http://hotnjuicycrawfish.com" + item.a['href']
		except:
			continue

		logger.info(page_link)
		city_text = item.find('h4').text
		city = city_text[:city_text.find(',')].title()
		if "Planet" in city:
			city = "Las Vegas"

		req = requests.get(page_link, headers=headers)

		try:
			new_base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		location_name = new_base.find('title').text
		location_name = location_name[:location_name.find("-")].strip()
		raw_data = new_base.find('div', attrs={'class': 'sub-text updates info _2-lines'}).text.replace("Â\xa0"," " ) 
		raw_address = raw_data[:raw_data.find(',')]
		street_address = "<INACCESSIBLE>"
		state = raw_data[raw_data.rfind(',')+1:raw_data.rfind(' ')].strip()
		zip_code = raw_data[raw_data.rfind(' '):].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = new_base.find('div', attrs={'class': 'information w-clearfix'}).text
		except:
			try:
				phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", str(new_base))[1]
			except:
				phone = "<MISSING>"
		location_type = "<MISSING>"
		link = new_base.find('iframe')['src']
		start_point = link.find("2d") + 2
		longitude = link[start_point:link.find('!',start_point)]
		long_start = link.find('!',start_point)+3
		latitude = link[long_start:link.find('!',long_start)]

		hours_of_operation = new_base.find('div', attrs={'class': 'update pad-bottom'}).get_text(separator=u' ').replace("\n"," ").replace("  "," ").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		data.append([locator_domain, location_name, raw_address, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
