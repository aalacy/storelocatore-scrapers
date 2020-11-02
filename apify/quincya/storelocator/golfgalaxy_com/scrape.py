from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('golfgalaxy_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://stores.golfgalaxy.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
		logger.info("Got today page")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	main_links = []
	main_items = base.find(class_="contentlist").find_all('li')
	for main_item in main_items:
		main_link = main_item.a['href']
		main_links.append(main_link)

	final_links = []
	for main_link in main_links:
		logger.info()
		logger.info("Processing State: " + main_link)
		req = session.get(main_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		next_items = base.find(class_="contentlist").find_all('li')
		for next_item in next_items:
			next_link = next_item.a['href']
			logger.info("Processing City: " + next_link)

			next_req = session.get(next_link, headers = HEADERS)
			time.sleep(randint(1,2))
			try:
				next_base = BeautifulSoup(next_req.text,"lxml")
			except (BaseException):
				logger.info('[!] Error Occured. ')
				logger.info('[?] Check whether system is Online.')

			final_items = next_base.find_all('span', attrs={'itemprop': 'streetAddress'})
			for final_item in final_items:
				final_link = final_item.find('a', attrs={'linktrack': 'Landing page'})['href']
				final_links.append(final_link)
	
	data = []
	for final_link in final_links:
		final_req = session.get(final_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(final_req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		locator_domain = "golfgalaxy.com"

		location_name = item.find("h1").text.strip().title()
		logger.info(location_name)

		street_address = item.find('span', attrs={'itemprop': 'containedIn'}).text.strip()
		try:
			street_address = street_address + " " + item.find('span', attrs={'itemprop': 'streetAddress'}).text.strip()
			street_address = street_address.strip()
		except:
			pass
		
		city = item.find('span', attrs={'itemprop': 'addressLocality'}).text.strip()
		state = item.find('span', attrs={'itemprop': 'addressRegion'}).text.strip()
		zip_code = item.find('span', attrs={'itemprop': 'postalcode'}).text.strip()
		country_code = "US"
		store_number = "<MISSING>"
		
		location_type = "<MISSING>"

		try:
			phone = item.find(class_="phone").text.strip()
		except:
			phone = "<MISSING>"

		latitude = item.find('meta', attrs={'property': 'place:location:latitude'})['content']
		longitude = item.find('meta', attrs={'property': 'place:location:longitude'})['content']

		raw_hours = item.find(id="all_hours_table").find_all('tr')
		hours = ""
		hours_of_operation = ""

		try:
			for hour in raw_hours:
				hours = hours + " " + hour.text.replace("\t","").replace("\n"," ").strip()
			hours_of_operation = (re.sub(' +', ' ', hours)).strip()
		except:
			pass
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
