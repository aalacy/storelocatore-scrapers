from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.belletire.com/stores"

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
		
	stores = base.find_all(class_="store-details__info")

	script = base.find('script', attrs={'type': "application/json"}).text
	script = script[script.find("{"):script.rfind("}")+1].strip() 
	store_data = json.loads(script)['props']['allStores']

	data = []
	found_poi = []
	for item in store_data:
		locator_domain = "belletire.com"

		location_name = item['Name']
		street_address = item['Address']
		location = location_name + "_" + street_address

		if location in found_poi:
			continue
		print(location_name)

		
		city = item['City']
		state = item['State']
		zip_code = item['ZipCode']
		country_code = 'US'
		phone = item['Phone']
		store_number = item['Id']
		location_type = "<MISSING>"
		latitude = item['Location']['Latitude']
		longitude = item['Location']['Longitude']
		
		raw_hours = item['StoreHours']
		hours = ""
		hours_of_operation = ""
		try:
			for hour in raw_hours:
				clean_hour = hour['Day'] + " " + hour['Opens'] + " - " + hour['Closes']
				hours = hours + " " + clean_hour
			hours_of_operation = hours.strip()
		except:
			hours_of_operation = "<MISSING>"
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		page_url = base_link

		found_poi.append(location)

		data.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
