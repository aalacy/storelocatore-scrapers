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

	base_link = "https://www.fountaintire.com/umbraco/api/locations/get"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	# Request post
	payload = {'latitude': '51.253775',
				'longitude': '-85.323214',
				'radius': '5000',
				'services':''}

	req = session.post(base_link,headers=HEADERS,data=payload)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	js = base.text
	store_data = json.loads(js)

	ids = []
	for store in store_data:
		ids.append(store["id"])
	
	data = []
	for id_num in ids:
		final_link = "https://www.fountaintire.com/stores/details/" + id_num
		print(final_link)
		req = session.get(final_link, headers = HEADERS)
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')
			
		locator_domain = "fountaintire.com"

		script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').replace("\r","").strip()
		store = json.loads(script)

		location_name = store['name']
		street_address = store['address']['streetAddress']
		city = store['address']['addressLocality']
		state = store['address']['addressRegion']
		zip_code = store['address']['postalCode']
		country_code = "CA"
		store_number = final_link.split("/")[-1]
		location_type = base.find(id="tab-features").text.strip().replace("\n",",")
		phone = store['telephone']

		hours_of_operation = ""
		raw_hours = store['openingHoursSpecification']
		for hours in raw_hours:
			day = hours['dayOfWeek']
			if len(day[0]) != 1:
				day = ' '.join(hours['dayOfWeek'])
			opens = hours['opens']
			closes = hours['closes']
			if opens != "" and closes != "":
				clean_hours = day + " " + opens + "-" + closes
				hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']
		page_url = store["url"]
		data.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
