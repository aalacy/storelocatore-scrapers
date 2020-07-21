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
	
	base_link = "https://stores.staples.ca/"

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

	all_scripts = base.find_all('script')
	for script in all_scripts:
		if "coordinates" in str(script):
			script = script.text.replace('\n', '').strip()
			break

	js_data = script[script.find('FeatureCollection')+30:script.rfind('}}]},')+3]
	js_data = json.loads(js_data)

	links = []
	for i in js_data: 
		link = "https://stores.staples.ca/" + i['properties']['slug']
		links.append(link)

	data = []
	for i, link in enumerate(links):
		print("Link %s of %s" %(i+1,len(links)))
		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(req.text,"lxml")
			print(link)
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		all_scripts = item.find_all('script', attrs={'type': "application/ld+json"})
		for script in all_scripts:
			if "latitude" in str(script):
				script = script.text.replace('\n', '').strip()
				break

		store = json.loads(script)

		locator_domain = "stores.staples.ca"
		location_name = store['name'] + " " + store['branchCode']
		street_address = store['address']['streetAddress'].replace(',','').strip()
		city = store['address']['addressLocality']
		title = item.title.text
		state = title[title.find("|")-4:title.find("|")].strip()
		zip_code = store['address']['postalCode']

		country_code = "CA"
		store_number = store['branchCode'].replace("CA-","").strip()
		
		location_type = "<MISSING>"
		phone = store['telephone']

		hours_of_operation = ""
		raw_hours = store['openingHoursSpecification']
		for hours in raw_hours:
			day = hours['dayOfWeek']
			opens = hours['opens']
			closes = hours['closes']
			clean_hours = day + " " + opens + "-" + closes
			hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
