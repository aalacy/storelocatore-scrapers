from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://www.paxsonoil.com/locations.htm"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = items = base.find_all("table")[5].find_all("tr")[1:]
	locator_domain = "paxsonoil.com"

	for item in items:

		raw_address = item.find_all("td")[1].text.strip().split("\n") 
		street_address = raw_address[-3].strip()
		street_address = (re.sub(' +', ' ', street_address)).strip()
		city_line = raw_address[-2].strip()
		city_line = (re.sub(' +', ' ', city_line)).strip()
		city = city_line[:-8].strip()
		state = city_line[-8:-6].strip()
		zip_code = city_line[-6:].strip()
		location_name = "Paxson Oil - " + city
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = item.find_all("td")[-1].text.strip()
		hours_of_operation = item.find_all("td")[-3].text.replace("\n"," ").replace("\t","").replace("Fri","Fri ").replace("Wed","Wed ").replace("pm","pm ").strip()
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
		if "open 24" in hours_of_operation.lower():
			hours_of_operation = "Open 24 hours"

		map_link = item.a['href']
		req = session.get(map_link, headers = HEADERS)
		maps = BeautifulSoup(req.text,"lxml")
		try:
			raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
			longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
