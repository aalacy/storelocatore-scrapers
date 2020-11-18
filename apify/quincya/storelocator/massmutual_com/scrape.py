from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('massmutual_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = 'https://financialprofessionals.massmutual.com/us'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	all_links = []
	found_poi = []
	
	states = base.find(class_="four-two-one list-states").find_all("a")
	locator_domain = "massmutual.com"

	for state in states:
		logger.info("Getting links for State: " + state.text)
		state_link = "https://financialprofessionals.massmutual.com" + state["href"]
		req = session.get(state_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		cities = base.find(class_="four-two-one list-cities").find_all("a")
		for city in cities:
			city_link = "https://financialprofessionals.massmutual.com" + city["href"]
			req = session.get(city_link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")

			raw_links = base.find_all(class_="mm-advisor-card mm-advisor-card--agency")
			for raw_link in raw_links:
				link = "https://financialprofessionals.massmutual.com" + raw_link.a["href"]
				if link not in all_links:
					all_links.append(link)

	logger.info("Processing " + str(len(all_links)) + " potential links ..")
	for link in all_links:
		# print(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		try:
			location_name = base.find(class_="h3 es-agency-name").text.strip()
		except:
			continue

		street_address = base.find(class_="es-street-address").text.strip()

		loc_str = location_name + "_" + street_address
		if loc_str in found_poi:
			continue

		found_poi.append(loc_str)
		
		city = base.find(class_="es-address-locality").text.strip()
		state = base.find(class_="es-address-region").text.strip().upper()
		zip_code = base.find(class_="es-postal-code").text.replace("050301","05301").strip()
		if len(zip_code) == 4:
			zip_code = "0" + zip_code
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = base.find(class_="es-telephone").text.strip()
		if not phone:
			phone = "<MISSING>"
		hours_of_operation = "<MISSING>"
		lat = float(base.find(class_="es-street-address")["data-geo"].split(",")[0])
		lon = float(base.find(class_="es-street-address")["data-geo"].split(",")[1])

		latitude = format(lat, '.4f')
		longitude = format(lon, '.4f')

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
