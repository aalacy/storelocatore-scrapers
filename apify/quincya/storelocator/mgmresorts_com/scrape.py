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
	
	base_link = "https://www.mgmresorts.com/en/destinations.html"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	all_links = []

	items = base.find_all(class_="grid-item m-1-2 l-1-4 rte-3block")[:2]
	locator_domain = "mgmresorts.com"

	for item in items:
		links = item.find_all("a")
		for i in links:
			if "http" not in i["href"]:
				link = "https://www.mgmresorts.com" + i["href"]
			else:
				link = i["href"]
			all_links.append(link)

	for link in all_links:
		if "mgmresorts.com" not in link:
			continue

		print(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.title.text.strip()

		if "hotels" in link:
			raw_address = base.find(class_="details-text grid-item width-1 m-1-2 l-5-16 xl-3-8").p.text.strip().split(",")
			street_address = raw_address[0].strip()
			if street_address == "3772 Las Vegas Blvd S":
				city = "Las Vegas"
				state = "NV"
				zip_code = "89109"
			else:
				try:
					city = raw_address[1].strip()
					state_line = raw_address[2].strip().split(" ")
					state = state_line[0].strip()
					zip_code = state_line[1].strip()
				except:
					raw_address = base.find_all(class_="amenity-container")[2].text.replace("Address","").strip().split("\n")
					street_address = raw_address[0].strip()
					city_line = raw_address[1].split(",")
					city = city_line[0].strip()
					state = city_line[1].strip()[:-6].strip()
					zip_code = city_line[1][-6:].strip()
			phone = base.find(class_="hours").text.strip()
			if "and" in phone:
				phone = phone[:phone.find("and")].strip()
		else:
			raw_address = base.find(class_="address-text").text.strip().split("\n")
			street_address = raw_address[0].strip()
			city_line = raw_address[1].split(",")
			city = city_line[0].strip()
			state = city_line[1].strip()[:-6].strip()
			zip_code = city_line[1][-6:].strip()
			phone = base.find(class_="phone-nbr").text.strip()
		street_address = street_address.replace("1777 3rd Ave","1777 Third St.")
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		hours_of_operation = "<MISSING>"
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
