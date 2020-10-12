from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="sothebysrealty.com")

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
			"HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
			"MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
			"NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
			"SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

	data = []
	found_poi = []

	locator_domain = "sothebysrealty.com"

	for state in states:
		log.info("Getting data for State: " + state)
		page_next = True
		base_link = "https://www.sothebysrealty.com/eng/offices/" + state + "-usa/30-pp"

		while page_next:
			# print(base_link)
			req = session.get(base_link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")

			links = base.find_all('link', attrs={'itemprop': 'mainEntityOfPage'})
			names = base.find_all(class_="org url") 
			streets = base.find_all(class_="contact-card__address adr")
			cities = base.find_all(class_="locality city")
			states = base.find_all(class_="region")
			zips = base.find_all(class_="postal-code")
			phones = base.find_all(class_="contact-card__phones")

			# Lat/Lng
			all_scripts = base.find_all('script')
			for script in all_scripts:
				if ",lng:" in str(script):
					script = str(script)
					break

			try:
				geos = re.findall(r'lat:[0-9]{2}\.[0-9]+,lng:-[0-9]{2,3}\.[0-9]+', script)
			except:
				page_next = False
				continue
			for i in range(len(links)):
				link = "https://www.sothebysrealty.com" + links[i]["href"]
				if link in found_poi:
					continue
				found_poi.append(link)
				location_name = names[i].span.img["alt"].replace("&amp;","&").encode("ascii", "replace").decode().replace("?","")

				try:
					street_address = streets[i].find(class_="street-address").text + " " + streets[i].find(class_="address").text
				except:
					street_address = streets[i].find(class_="street-address").text.strip()

				street_address = (re.sub(' +', ' ', street_address)).strip()
				city = cities[i].text.strip()
				state = states[i].text.strip()
				zip_code = zips[i].text.strip()
				phone = phones[i].find_all("a")[-1]["href"].replace("tel:","")
				country_code = "US"
				store_number = "<MISSING>"
				location_type = "<MISSING>"
				hours_of_operation = "<MISSING>"
				latitude = geos[i].split(",")[0].split(":")[1]
				longitude = geos[i].split(",")[1].split(":")[1]

				data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

			# Check for next page
			try:
				base_link = "https://www.sothebysrealty.com" + base.find('a', attrs={'aria-label': 'Next'})["href"]
				if base_link == "https://www.sothebysrealty.com#":
					page_next = False
			except:
				page_next = False

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
