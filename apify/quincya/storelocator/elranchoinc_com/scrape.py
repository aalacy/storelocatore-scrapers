import csv
import time
import re
from sgrequests import SgRequests
from bs4 import BeautifulSoup
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

	base_link = "https://elranchoinc.com/wp-admin/admin-ajax.php"
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	
	data = []
	payload = { 'lat': '31.9685988', 
				'lng': '-99.9018131', 
				'store_locatore_search_radius': '500', 
				'action': 'make_search_request'}

	base_link = "https://elranchoinc.com/wp-admin/admin-ajax.php"
	response = session.post(base_link,headers=HEADERS,data=payload)
	base = BeautifulSoup(response.text,"lxml")

	fin_script = ""
	all_scripts = base.find_all('script')
	for script in all_scripts:
		if "lng" in str(script):
			fin_script = script.text.replace('\\', '').replace('"/>', '').replace('"http', '').replace('">','').replace('class="','class=').replace('" class',' class').replace("\n","").strip()
			break

	js = fin_script.split('locations":')[-1].split("};  ")[0].strip()
	stores = json.loads(js)
	items = base.find_all(class_="store-locator-item")
	
	locator_domain = "elranchoinc.com"

	for i in range(len(stores)):
		store = stores[i]
		item = items[i]
		location_name = item.find(class_="wpsl-name").text.strip()
		street_address = item.find(class_="wpsl-address").text.strip()
		city_line = item.find(class_="wpsl-city").text.strip().split(",")
		city = city_line[0]
		state = city_line[1].split()[0].strip()
		try:
			zip_code = city_line[1].split()[1].strip()
		except:
			zip_code = "<MISSING>"
		country_code = "US"
		store_number = item["id"]
		location_type = "<MISSING>"
		phone = item.find(class_="wpsl-phone").text.strip()
		hours_of_operation = "<MISSING>"
		latitude = store['lat']
		longitude = store['lng']
		link = "https://elranchoinc.com/stores-2/"
		
		# Store data
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
