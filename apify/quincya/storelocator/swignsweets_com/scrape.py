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
	
	base_link = "https://www.swignsweets.com/?post_type=wc_pickup_location"

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

	# Find raw coords
	all_scripts = base.find_all('script')
	for script in all_scripts:
		if "lng" in str(script):
			script = str(script)
			break

	maps = re.findall(r'api=1&destination.{30}', script)
	geos = re.findall(r'lat".{50}', script)[1:-2]

	items = base.find_all(class_="Card__details")
	locator_domain = "swignsweets.com"

	for item in items:

		location_name = item.h4.text.replace("’","'").strip()
		
		raw_address = item.find(class_="address").text.replace(" St. George ",",St. George,").replace("180 Logan","180, Logan").replace(", USA","").split(",")
		street_address = " ".join(raw_address[:-2]).strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()
		city = raw_address[-2].strip()
		state = raw_address[-1].strip()[:-6].strip()
		zip_code = raw_address[-1][-6:].strip()
		if not state:
			state = zip_code
			zip_code = "<MISSING>"
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		try:
			phone = item.find(class_="phone").text
		except:
			phone = "<MISSING>"
		hours_of_operation = item.find(class_="location-schedule").text.strip().replace("\n","")
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()

		orig_map = item.a["href"].split("destination=")[-1]
		latitude = "<MISSING>"
		longitude = "<MISSING>"
		for i, raw_map in enumerate(maps):
			if raw_map.split("destination=")[-1] in orig_map:
				raw_geo = geos[i]
				latitude = raw_geo.split(":")[1].split(",")[0]
				longitude = raw_geo.split(":")[2].split("}")[0]
				break
		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
