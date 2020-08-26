from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
import time
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

	base_link = "https://germanamerican.com/locations/locations-overview/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	locator_domain = "germanamerican.com"

	items = base.find_all(class_="cta-lnk lnk")

	for i, item in enumerate(items[60]):
		print("Link %s of %s" %(i+1,len(items)))
		link = "https://germanamerican.com" + item["href"]
		print(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		try:
			script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
			store = json.loads(script)
			json_exists = True
		except:
			json_exists = False

		if json_exists:
			location_name = store['name'] + " - " + base.h1.text.strip()
			street_address = store['address']['streetAddress']
			city = store['address']['addressLocality']
			state = store['address']['addressRegion']
			zip_code = store['address']['postalCode']
			country_code = store['address']['addressCountry']
			phone = store['telephone']
		else:
			location_name = "German American Bank - " + base.h1.text.strip()
			street_address = base.h1.text.strip()
			raw_address = base.find(class_="f-h4").text.split(",")
			city = raw_address[0].strip()
			state = raw_address[1].split()[0].strip()
			zip_code = raw_address[1].split()[1].strip()
			country_code = "US"
			phone = ""
			try:
				phone = base.find(class_="phone").text.strip()
			except:
				pass
		
		if not phone:
			try:
				phone = base.find(class_="branch_contact_info clearfix").dd.text.strip()
			except:
				phone = "<MISSING>"
		store_number = "<MISSING>"
		location_type = ""
		raw_types = base.find_all(class_="filter-service-name")
		for raw_type in raw_types:
			location_type = location_type + "," + raw_type.text.strip()
		location_type = location_type[1:]
		hours_of_operation = base.find(class_="branch_hours_days clearfix").text.replace("PM","PM ").replace("Closed","Closed ").strip()

		map_link = base.find(id="sec-sidebar").find(class_="btn cta-btn")["href"]
		driver.get(map_link)
		time.sleep(8)

		try:
			map_link = driver.current_url
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"
		
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
