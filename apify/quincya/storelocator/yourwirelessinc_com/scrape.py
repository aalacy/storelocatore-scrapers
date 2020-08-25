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
	
	base_link = "https://yourwirelessinc.com/"

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
	found_poi = []

	items = base.find(id="all").find_all(class_="item-details pull-left")
	locator_domain = "yourwirelessinc.com"

	for item in items:

		location_name = item.h5.text.strip()

		raw_data = item.text.strip().replace("\t","").replace("\n\n","\n").split("\n")
		
		street_address = raw_data[1].replace("Unit", " Unit").replace("Suite", " Suite").strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()
		if street_address in found_poi:
			continue

		found_poi.append(street_address)
		city_line = raw_data[2].strip().split(",")
		city = city_line[0].strip()
		state = city_line[-1].strip().split()[0].strip()
		zip_code = city_line[-1].strip().split()[1].strip()
		if zip_code == "36054":
			zip_code = "23093"
		if zip_code == "100002":
			zip_code = "10002"
		if len(zip_code) < 5:
			zip_code = "0" + zip_code
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = raw_data[-1].replace("Tel :","").strip()
		hours_of_operation = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
