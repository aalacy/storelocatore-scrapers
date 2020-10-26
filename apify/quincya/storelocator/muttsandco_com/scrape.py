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
	
	base_link = "https://muttsandco.com/pages/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find(id="megamenu_items-locations").find_all("a")
	locator_domain = "muttsandco.com"

	for item in items:
		link = "https://muttsandco.com" + item["href"]

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = "Mutts & Co - " + base.h1.text.strip()
		# print(link)
		
		raw_address = str(base.find(class_="col-md-11")).replace("<br/","").replace("</div","").split(">")[1:-1]
		street_address = raw_address[0].strip()
		city_line = raw_address[1].strip().split(",")
		city = city_line[0].strip()
		state = city_line[-1].strip().split()[0].strip()
		zip_code = city_line[-1].strip().split()[1].strip()

		country_code = "US"
		store_number = "<MISSING>"
		
		location_type = base.find(class_="col-md-8 col-md-offset-2").text.replace("Services","").strip().replace("\n\n\n",",").replace("\n","").replace(",,",",")
		location_type = (re.sub(' +', ' ', location_type)).strip()
		try:
			phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", str(base))[0]
		except:
			phone = "<MISSING>"

		hours_of_operation = base.find_all(class_="col-md-11")[-1].text.replace("Hours","").replace("–","-").strip()

		try:
			map_link = base.iframe["src"]
			lat_pos = map_link.rfind("!3d")
			latitude = map_link[lat_pos+3:map_link.find("!",lat_pos+5)].strip()
			lng_pos = map_link.find("!2d")
			longitude = map_link[lng_pos+3:map_link.find("!",lng_pos+5)].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
