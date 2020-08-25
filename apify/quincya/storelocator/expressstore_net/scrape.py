from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
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
	
	base_link = "https://expressstore.net/wp-admin/admin-ajax.php?action=store_search&lat=40.71278&lng=-74.00597&max_results=25&search_radius=100&autoload=1"

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
	locator_domain = "expressstore.net"

	store_data = json.loads(base.text)
	for store in store_data:
		location_name = store['store'].replace("–","-")
		street_address = store['address'].strip()
		city = store['city']
		state = store['state']
		zip_code = store['zip']
		country_code = "US"
		store_number = store['id']
		location_type = "<MISSING>"
		phone = store['phone']
		hours_of_operation = store["hours"].replace("day","day ").replace("PM","PM ").replace("Closed","Closed ").strip()
		latitude = store['lat']
		longitude = store['lng']
		if not latitude:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		link = store["permalink"]
		
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
