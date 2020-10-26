from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint


def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.gordonbierschrestaurants.com/locations"

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

	items = base.find_all(class_="css-1p5rxv9 exjileg1")
	locator_domain = "gordonbierschrestaurants.com"

	for item in items:
		raw_data = item.text.split("\n")

		location_name = item.h5.text
		print(location_name)
		
		raw_address = item.p.text
		city = location_name
		street_address = raw_address[:raw_address.find(city)].strip()
		state = raw_address.split(',')[-1].split()[0].strip()
		zip_code = raw_address.split(',')[-1].split()[1].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "Main Location"
		phone = item.h6.text
		hours_of_operation = item.find_all('p')[-1].text
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])


	# Airport Locations
	
	base_link = "https://www.gordonbierschrestaurants.com/airport-locations"

	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	items = base.find(class_="css-nsigw3 eh6u8tz2").find_all('p')

	for i, item in enumerate(items):
		if "Taiwan" in item.text:
			break
		if "strong" in str(item):
			location_name = item.text
			print(location_name)
		
			raw_address = items[i+1].text
			city = raw_address.split(",")[-2].strip()
			street_address = raw_address[:raw_address.rfind(city)].strip()[:-1]
			state = raw_address.split(',')[-1].split()[0].strip()
			zip_code = raw_address.split(',')[-1].split()[1].strip()
			country_code = "US"
			store_number = "<MISSING>"
			location_type = "Airport Location"
			phone = raw_address.split(',')[-1].split()[2].strip()
			hours_of_operation = "<MISSING>"
			latitude = "<MISSING>"
			longitude = "<MISSING>"

			data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
