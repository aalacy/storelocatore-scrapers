from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

from sgselenium import SgSelenium

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	driver = SgSelenium().chrome()
	time.sleep(2)
	
	base_link = "https://www.althotels.com/en/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
		print("Got today page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	data = []
	items = base.find_all(class_="evfhd7u1 css-xkuyuq")

	locator_domain = "germainhotels.com"

	for item in items:
		link = "https://www.germainhotels.com" + item['href']

		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
			# print(link)
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')
		
		location_name = base.find(class_="css-11ftk7z evn0nt63").text.strip()
		print(location_name)
		
		raw_address = base.find(class_='css-6nfh5n evn0nt64').text.split(",")
		if len(raw_address) > 4:
			street_address = raw_address[0].strip() + " " + raw_address[1].strip()
		else:
			street_address = raw_address[0]

		city = raw_address[-3].strip()
		state = raw_address[-2].strip()
		zip_code = base.find(class_="css-epvm6 evn0nt65").text.strip()
		if zip_code == "TG2 0G1":
			zip_code = "T2G 0G1"
		if zip_code == "K1P OC8":
			zip_code = "K1P 0C8"

		country_code = "CA"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		phone = base.find(class_="css-k4gcyp e1fndnol3").text.strip()

		# Maps
		map_link = base.find(class_="css-1a39in1")['href']
		if "maps" in map_link:
			try:
				driver.get(map_link)
				time.sleep(randint(6,8))
				try:
					map_link = driver.current_url
					at_pos = map_link.rfind("@")
					latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
					longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
				except:
					latitude = "<INACCESSIBLE>"
					longitude = "<INACCESSIBLE>"
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"
		else:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		hours_of_operation = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
