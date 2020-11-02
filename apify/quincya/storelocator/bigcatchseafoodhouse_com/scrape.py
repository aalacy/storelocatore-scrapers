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
	
	base_link = "https://bigcatchseafoodhouse.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all(class_="rank-math-review-data")
	locator_domain = "bigcatchseafoodhouse.com"

	for item in items:

		street_address = item.find(class_="contact-address-address").text.strip()
		city = item.find(class_="contact-address-locality").text.strip()
		state = item.find(class_="contact-address-region").text.strip()
		zip_code = item.find(class_="contact-address-postalcode").text.strip()

		location_name = "Big Catch Seafood House " + city
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = item.find_all("a")[1].text.strip()
		hours_of_operation = " ".join(list(item.find(class_="rank-math-contact-hours-details rank-math-gear-snippet-content").stripped_strings)).encode("ascii", "replace").decode().replace("?","-")

		map_link = item.a['href']
		# Maps
		req = session.get(map_link, headers = HEADERS)
		maps = BeautifulSoup(req.text,"lxml")

		try:
			raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
			latitude = raw_gps.split("=")[-1].split(",")[0]
			longitude = raw_gps.split("=")[-1].split(",")[1]
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		if "765 N. Milliken" in street_address:
			latitude = "34.070946"
			longitude = "-117.5614592"			

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
