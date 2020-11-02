from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('getregionalcash_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://branches.regionalfinance.com/index.html"

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
	main_items = base.find_all(class_="c-directory-list-content-item-link")
	for main_item in main_items:
		main_link = "https://branches.regionalfinance.com/" + main_item['href']
		main_links.append(main_link)


	final_links = []
	for next_link in main_links:
		logger.info("Processing: " + next_link)
		req = session.get(next_link, headers = HEADERS)
		# time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')
		
		next_items = base.find_all(class_="c-directory-list-content-item")
		for next_item in next_items:
			count = next_item.find(class_="c-directory-list-content-item-count").text.replace("(","").replace(")","")
			link = "https://branches.regionalfinance.com/" + next_item.find(class_="c-directory-list-content-item-link")['href']
			if count == "1":
				final_links.append(link)
			else:
				next_req = session.get(link, headers = HEADERS)
				# time.sleep(randint(1,2))
				try:
					next_base = BeautifulSoup(next_req.text,"lxml")
				except (BaseException):
					logger.info('[!] Error Occured. ')
					logger.info('[?] Check whether system is Online.')

				other_links = next_base.find_all('a', attrs={'data-ya-track': 'visitsite'})
				for other_link in other_links:
					link = "https://branches.regionalfinance.com/" + other_link['href'].replace("../","")
					final_links.append(link)
	
	data = []
	for final_link in final_links:
		final_req = session.get(final_link, headers = HEADERS)
		# time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(final_req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		locator_domain = "getregionalcash.com"

		city = item.find('span', attrs={'itemprop': 'addressLocality'}).text.strip()
		location_name_geo = item.find(class_="LocationName-geo").text.strip()

		if "1719 Wilma Rudolph" in location_name_geo:
			location_name_geo = city

		location_name = item.find(class_="LocationName-brand").text.strip() + " " + location_name_geo
		logger.info(location_name)

		street_address = item.find(class_="c-address-street-1").text.replace("\u200b","").strip()
		try:
			street_address = street_address + " " + item.find(class_="c-address-street-2 break-before").text.replace("\u200b","").strip()
			street_address = street_address.strip()
		except:
			pass
		
		state = item.find(class_="c-address-state").text.strip()
		zip_code = item.find(class_="c-address-postal-code").text.strip()
		country_code = "US"
		store_number = "<MISSING>"
		
		location_type = "<MISSING>"

		try:
			phone = item.find(id="telephone").text.strip()
		except:
			phone = "<MISSING>"

		latitude = item.find('meta', attrs={'itemprop': 'latitude'})['content']
		longitude = item.find('meta', attrs={'itemprop': 'longitude'})['content']

		hours_of_operation = ""
		raw_hours = item.find(class_="c-location-hours-details")
		raw_hours = raw_hours.find_all("td")

		hours = ""
		hours_of_operation = ""

		try:
			for hour in raw_hours:
				hours = hours + " " + hour.text.strip()
			hours_of_operation = (re.sub(' +', ' ', hours)).strip()
		except:
			pass
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		location_data = [locator_domain, final_link, location_name, street_address, city, state, zip_code,
						country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

		data.append(location_data)

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()