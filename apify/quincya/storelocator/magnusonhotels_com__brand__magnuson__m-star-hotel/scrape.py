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

	base_link = "https://www.magnusonhotels.com/brand/m-star-hotel/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	final_links = []
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		main_base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')
	
	items = main_base.find_all(class_="hoteltop")
	
	for item in items:
		link = item.a["href"].split("/")[-1]
		if link not in final_links:
			final_links.append(link)

	try:
		last_page = int(main_base.find_all(class_="page-numbers")[-2].text)
		for page_num in range(2,last_page+1):
			page_link = base_link + "page/" + str(page_num)
			req = session.get(page_link, headers = HEADERS)
			time.sleep(randint(1,2))
			try:
				main_base = BeautifulSoup(req.text,"lxml")
			except (BaseException):
				print('[!] Error Occured. ')
				print('[?] Check whether system is Online.')
	
			items = main_base.find_all(class_="hoteltop")
			
			for item in items:
				link = item.a["href"].split("/")[-1]
				if link not in final_links:
					final_links.append(link)
	except:
		pass

	for link in final_links:
		final_link = "https://api.magnusonhotels.com/api/v1/hotels/find/" + link
		req = session.get(final_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		store = json.loads(base.text)["result"]
		location_name = store["name"]
		locator_domain = "magnusonhotels.com"
		raw_address = store["addresses"].split(",")
		street_address = raw_address[-1].strip()
		city = raw_address[0].strip()
		state = raw_address[1].strip()
		if not state:
			state = "<MISSING>"
		zip_code = store["zipcode"]
		country_code = "US"
		store_number = store["id"]
		raw_types = store["amenities"]
		location_type = ""
		for raw_type in raw_types:
			location_type = location_type + "," + raw_type["name"]
		location_type = location_type[1:]
		phone = store["phone"]
		if phone[:1] != "1" or "London" in state or "BA" in state:
			continue
		hours_of_operation = "<MISSING>"
		latitude = store["lat"]
		longitude = store["lng"]

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
