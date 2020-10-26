from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import json
import re
from random import randint


def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.marinerfinance.com/state/"

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

	main_links = []
	main_items = base.find('table').find_all('a')
	for main_item in main_items:
		main_link = main_item['href']
		main_links.append(main_link)

	final_links = []
	for main_link in main_links:
		req = session.get(main_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
			print(main_link)
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		final_items = base.find_all(class_="post-box__foot")
		for final_item in final_items:
			final_link = final_item.a['href']
			final_links.append(final_link)

	data = []
	total_links = len(final_links)
	for i, final_link in enumerate(final_links):
		print("Link %s of %s" %(i+1,total_links))
		final_req = session.get(final_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(final_req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		locator_domain = "marinerfinance.com"

		location_name = base.h1.text.strip()
		print(location_name)

		item = base.find(class_="type")
		script = item.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
		raw_data = json.loads(script)

		street_address = raw_data['address']['streetAddress']
		city = raw_data['address']['addressLocality']
		state = raw_data['address']['addressRegion']
		zip_code = raw_data['address']['postalCode']
		if street_address == "3225 N. 5th St. Highway":
			zip_code = "19605"
		if len(zip_code) == 4:
			zip_code = "0" + zip_code
			
		country_code = "US"
		store_number = re.findall('Branch Number: [0-9]+',str(item))[0].split(":")[1].strip()
		location_type = "<MISSING>"
		phone = raw_data['telephone']

		map_link = item.find("a", string="Directions")['href']
		req = session.get(map_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			maps = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		try:
			raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
			longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		hours_of_operation = item.find("ul").text.replace("\n"," ").strip()

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
