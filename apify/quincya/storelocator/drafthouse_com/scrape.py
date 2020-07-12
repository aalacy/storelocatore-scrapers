from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
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
	
	base_link = "https://drafthouse.com/markets"

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
	main_items = base.find_all(id="markets-page")
	for main_item in main_items:
		main_link = main_item['href'] + "/theaters"
		main_links.append(main_link)

	data = []
	for final_link in main_links:
		final_req = session.get(final_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(final_req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		locator_domain = "drafthouse.com"

		items = base.find(class_="medium-3 columns").find_all("li")

		for item in items:
			location_name = item.a.text.strip()
			
			if "Coming Soon" in location_name:
				continue

			print(location_name)
			raw_address = item.find_all("a")[-2].text.strip().split("\n")

			street_address = raw_address[0].strip()
			city = raw_address[1].strip().split(",")[0].strip()
			state = raw_address[1].strip().split(",")[1][:-6].strip()
			zip_code = raw_address[1].strip().split(",")[1][-6:].strip()
			country_code = "US"
			store_number = "<MISSING>"
			
			location_type = "<MISSING>"
			
			phone = item.find_all("a")[-1].text

			map_link = item.find_all("a")[-2]['href']
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

			hours_of_operation = "<MISSING>"

			data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
