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
	
	base_link = "https://www.johnnywas.com/store-locator"

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

	items = base.find_all(class_="individual-store-link")
	locator_domain = "johnnywas.com"

	for item in items:
		if "opening" in item.text.lower():
			continue

		link = "https://www.johnnywas.com" + item["href"]
		print(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.h1.text.strip()

		raw_data = base.find(class_="exact-address").text.split(",")

		try:
			street_address = raw_data[-5].strip() + " " + raw_data[-4].strip()
		except:
			street_address = raw_data[-4].strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()

		city = raw_data[-3].strip()
		state = raw_data[-2].strip()
		zip_code = raw_data[-1].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = base.find(class_="phone").text.strip()

		hours_of_operation = base.find(class_="schedule").text.replace("HOURS","").replace("\r \n"," ").strip()
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()

		try:
			map_link = base.find(class_="get-directions").a["href"]
			latitude = map_link.split("=")[-1].split(",")[0]
			longitude = map_link.split("=")[-1].split(",")[1]
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		if street_address == "3510 Galleria Suite 3325":
			latitude = "44.8770921"
			longitude = "-93.3612937"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
