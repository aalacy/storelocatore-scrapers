from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
import json

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://qualitymartnc.com/locations/"

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
	locator_domain = "qualitymartnc.com"

	all_scripts = base.find_all('script')
	for script in all_scripts:
		if "lng" in str(script):
			script = script.text.replace('\n', '').strip()
			break

	start_pos = script.find("wpgmaps_localize_marker_data")
	clean_script = script[start_pos+31:script.find("}}}",start_pos)+3]
	store_data = json.loads(clean_script)["1"]

	for store_num in store_data:
		store = store_data[store_num]
		location_name = store['title']
		print(location_name)
		
		raw_address = store['address'].split(",")
		street_address = " ".join(raw_address[:-2]).strip()
		city = raw_address[-2].strip()
		state = raw_address[-1].strip()[:-6].strip()
		zip_code = raw_address[-1][-6:].strip()

		country_code = "US"
		store_number = location_name.split("#")[1]
		
		raw_types = store['desc']
		location_type = raw_types[raw_types.rfind("strong>")+7:raw_types.rfind("</p>")].replace("<br />",",").replace(",,","")
		if location_type[:1] == ",":
			location_type = location_type[1:]
		if not location_type:
			location_type = "<MISSING>"
		try:
			phone = re.findall("[(\d)]{5} [\d]{3}-[\d]{4}", store['desc'])[0]
		except:
			phone = "<MISSING>"

		hours_of_operation = store['desc'].split("<br />")[2]
		if "Hours:" in hours_of_operation:
			hours_of_operation = hours_of_operation.replace("Hours:","").strip() + " daily"
		latitude = store['lat']
		longitude = store['lng']

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
