from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rubys_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.rubys.com/locations20/"

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

	data = []

	items = base.find_all(class_="link")
	locator_domain = "rubys.com"

	for item in items:
		link = item["href"]
		logger.info(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		if "locations" in link:
			raw_data = base.find(id="map-listing-wrap")

			location_name = raw_data.h1.text.replace("–","-").replace("’","'").replace(" - ","-").strip()
			raw_address = raw_data.find(class_="address").text.strip().split("\n")
			try:
				city = raw_address[-2].strip()
			except IndexError:
				raw_address = raw_data[2].split(",")
				city = raw_address[-2].strip()

			street_address = raw_address[0].strip()
			city_line = raw_address[-1].strip().split(",")
			city = city_line[0].strip()
			state = city_line[-1].strip().split()[0].strip()
			zip_code = city_line[-1].strip().split()[1].strip()
			if zip_code == "95086":
				zip_code = "85086"

			country_code = "US"
			store_number = "<MISSING>"
			location_type = "<MISSING>"
			phone = raw_data.find(class_="phone").text.strip()
			hours_of_operation = ""
			raw_hours = raw_data.find(class_="hours").find_all("p")
			for hour in raw_hours:
				if "hours" in hour.text.lower() or "closed" in hour.text.lower():
					hours = hour.text.replace("New Hours!","").replace("\xa0"," ").replace("\n"," ").replace("–","-").strip()
					if "Now" in hours:
						hours = hours[:hours.find("Now")].strip()
					hours_of_operation = (re.sub(' +', ' ', hours)).strip()
					break
			if hours_of_operation:
				if "call" in hours_of_operation.lower():
					hours_of_operation = "<MISSING>"
				elif len(hours_of_operation) < 15 and "pm" in hours_of_operation:
					hours_of_operation = hours_of_operation + " Daily"
			else:
				hours_of_operation = "<MISSING>"
			map_link = raw_data.find("a", string="Get Directions")["href"]
			req = session.get(map_link, headers = HEADERS)
			time.sleep(randint(1,2))
			maps = BeautifulSoup(req.text,"lxml")
			try:
				raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
				latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
				longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"
		else:
			if link == "https://rubysshakeshop.com":
				location_name = "Noho"
				street_address = "5072 Lankershim Blvd"
				city = "North Hollywood"
				state = "CA"
				zip_code = "91601"
				country_code = "US"
				store_number = "<MISSING>"
				location_type = "<MISSING>"
				phone = "(818) 747-2070"
				hours_of_operation = base.find(class_="footer-widget-single footer-widget-middle").find_all("p")[-1].text.replace("\n"," ")
				latitude = "34.165903"
				longitude = "-118.373542"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
