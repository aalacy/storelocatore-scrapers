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
	
	base_link = "https://lebanesetaverna.com/locations-%26-hours"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(2,4))
	try:
		base = BeautifulSoup(req.text,"lxml")
		print("Got today page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	data = []

	items = base.find_all('div', attrs={'data-ux': "ContentCard"})
	locator_domain = "lebanesetaverna.com"

	for item in items:

		location_name = item.h4.text.strip()
		print(location_name)
		
		raw_address = item.find_all("span")[-1].text.replace("\xa0","").strip()
		if "," not in raw_address:
			raw_address = item.find_all("span")[-2].text.strip()
		
		raw_address = raw_address.replace("VA,","VA").replace("  "," ")

		state = raw_address[raw_address.rfind(",")+1:raw_address.rfind(",")+4].strip()
		try:
			zip_code = re.findall(r' [0-9]{5}', raw_address)[0].strip()
		except:
			zip_code = "<MISSING>"

		raw_street_city = raw_address[:raw_address.rfind(",")]
		if "\n" in raw_street_city:
			raw_street_city = raw_street_city[raw_street_city.rfind('\n')+2:]

		city = raw_street_city.split()[-1].strip()
		if city == "SPRING":
			city = "SILVER SPRING"
		street_address = raw_street_city[:raw_street_city.rfind(city)].strip()

		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		try:
			phone = re.findall(r'[0-9]{3}.[0-9]{3}.[0-9]{4}', str(item))[0]
		except:
			try:
				phone = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', str(item))[0]
			except:
				phone = "<MISSING>"

		raw_hours = item.find_all('strong')
		hours_of_operation = ""
		for raw_hour in raw_hours:
			hours_of_operation = (hours_of_operation + " " + raw_hour.text.replace("\xa0","").strip()).strip()

		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
