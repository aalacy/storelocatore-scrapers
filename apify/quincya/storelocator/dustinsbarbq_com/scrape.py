from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.dustinsbarbq.com/locations/index"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find(id="geoLookupResults").find_all("a", string="More Info")
	locator_domain = "dustinsbarbq.com"

	for item in items:
		link = "https://www.dustinsbarbq.com" + item["href"]
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml").find(class_="z-float z-pv-40 subpage-bg")

		location_name = base.h1.text.strip()		
		raw_address = base.find(class_="z-t-23 elite z-mb-20 location-address").text.strip().split("\n")

		street_address = " ".join(raw_address[:-1]).strip()
		city_line = raw_address[-1].strip().split(",")
		city = city_line[0].strip()
		state = city_line[-1].strip().split()[0].strip()
		zip_code = city_line[-1].strip().split()[1].strip()
		country_code = "US"
		store_number = link.split("-")[-1][:-5]
		location_type = "<MISSING>"
		phone = base.find(class_="z-t-23 elite z-mb-20 location-phone").text.strip()
		hours_of_operation = base.find(class_="z-t-23 elite z-mb-20 location-hours").text.replace("Open","").strip()

		try:
			map_link = base.find("iframe")["src"]
			at_pos = map_link.rfind("!3d")
			latitude = map_link[at_pos+3:map_link.find("!",at_pos+5)].strip()
			longitude = map_link[map_link.find("!2d")+3:at_pos].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
