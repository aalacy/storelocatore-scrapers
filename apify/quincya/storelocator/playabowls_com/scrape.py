from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sgselenium import SgSelenium

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	driver = SgSelenium().chrome()
	time.sleep(2)
		
	base_link = "https://www.playabowls.com/locations/"

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

	items = base.find_all(class_="store__info")
	locator_domain = "playabowls.com"

	for i, item in enumerate(items):
		print("POI %s of %s" %(i+1,len(items)))
		location_name = item.h3.text.strip()
		print(location_name)
		
		raw_data = item.text.replace("Order Ahead","").replace("Get directions","").strip().split("\n")
		street_address = raw_data[-4].replace("Sea Isle City, NJ 08243","").replace("Doylestown PA 18901","").replace("Easton, PA 18045","").strip()
		city_line = raw_data[-3].split(",")
		city = city_line[0].strip()
		state = city_line[-1].strip()[:-6].strip()
		zip_code = city_line[-1][-6:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = raw_data[-2]
		hours_of_operation = raw_data[-1]
		if "," in phone:
			phone = "<MISSING>"
			street_address = " ".join(raw_data[1:-2]).strip()
			city_line = raw_data[-2].split(",")
			city = city_line[0].strip()
			state = city_line[-1].strip()[:-6].strip()
			zip_code = city_line[-1][-6:].strip()

		try:
			map_link = item.find("a", string = "Get directions")["href"]
			driver.get(map_link)
			time.sleep(7)

			try:
				map_link = driver.current_url
				at_pos = map_link.rfind("@")
				latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
				longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
			except:
				latitude = "<INACCESSIBLE>"
				longitude = "<INACCESSIBLE>"
			try:
				if "we could not calculate" in driver.find_element_by_class_name("section-directions-error-primary-text").text:
					latitude = "<MISSING>"
					longitude = "<MISSING>"
			except:
				pass
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
