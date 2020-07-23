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
	
	base_link = "https://locations.af247.com/"

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

	main_items = base.find(class_="full_location_list").find_all('a')

	final_links = []
	for main_item in main_items:
		link = main_item['href']
		if "id=" in link:
			final_links.append(link)
		else:
			req = session.get(link, headers = HEADERS)
			time.sleep(randint(1,2))
			try:
				base = BeautifulSoup(req.text,"lxml")
			except (BaseException):
				print('[!] Error Occured. ')
				print('[?] Check whether system is Online.')
		
			next_items = base.find(class_="full_location_list").find_all('a')
			for next_item in next_items:
				link = next_item['href']
				final_links.append(link)

	data = []
	for i, final_link in enumerate(final_links):
		print("Link %s of %s" %(i+1,len(final_links)))
		final_req = session.get(final_link, headers = HEADERS)
		print(final_link)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(final_req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		locator_domain = "af247.com"

		script = item.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
		store_data = json.loads(script)

		location_name = store_data['name']
		
		street_address = store_data['address']['streetAddress']
		city = store_data['address']['addressLocality']
		state = store_data['address']['addressRegion']
		zip_code = store_data['address']['postalCode']
		country_code = "US"
		store_number = store_data['@id']
		location_type = "<MISSING>"
		phone = store_data['telephone']

		latitude = store_data['geo']['latitude']
		longitude = store_data['geo']['longitude']

		hours_of_operation = item.find(class_="hours-body").text.replace("day","day ").replace("PM","PM ").strip()

		location_data = [locator_domain, final_link, location_name, street_address, city, state, zip_code,
						country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

		data.append(location_data)

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()