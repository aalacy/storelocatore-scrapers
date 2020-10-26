from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.kalahariresorts.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	data = []

	items = base.find_all(class_="blockPromo")
	locator_domain = "kalahariresorts.com"

	for item in items:

		link = "https://www.kalahariresorts.com" + item["href"] + "help/directions-maps-and-hours/"
		link2 = "https://www.kalahariresorts.com" + item["href"] + "help/contact-us/"
		
		req = session.get(link, headers = HEADERS)
		req2 = session.get(link2, headers = HEADERS)

		base = BeautifulSoup(req.text,"lxml")
		base2 = BeautifulSoup(req2.text,"lxml")

		try:
			phone = base2.find(class_="accordion-open").find_all("p")[1].text.replace("Local","").strip()
		except:
			continue

		location_name = item.text.strip()

		street_address = base.find(class_="footer-primary-container-section-info-address-street").text.strip()
		city_line = base.find(class_="footer-primary-container-section-info-address-cityState").text.strip().split(",")
		city = city_line[0].strip()
		state = city_line[1].strip()
		zip_code = base.find(class_="footer-primary-container-section-info-address-zip").text.strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"		
		hours_of_operation = base.find(class_="titleBox-bd quarantineContent").text.replace("Day7","Day 7").replace("k365","k 365").strip()

		try:
			map_link = base.find(class_="site").iframe["src"]
			lat_pos = map_link.rfind("!3d")
			latitude = map_link[lat_pos+3:map_link.find("!",lat_pos+5)].strip()
			lng_pos = map_link.find("!2d")
			longitude = map_link[lng_pos+3:map_link.find("!",lng_pos+5)].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
