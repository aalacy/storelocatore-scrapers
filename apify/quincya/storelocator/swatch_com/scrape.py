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

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	countries = ['United States','Canada']
	codes = ['us','ca']

	for i, country in enumerate(countries):
		# Request post
		payload = {'searchinput': country}
		code = codes[i]

		base_link = "https://www.swatch.com/en_" + code + "/api/storelocator/v2/search"
		response = session.post(base_link,headers=HEADERS,data=payload)

		base = BeautifulSoup(response.text,"lxml")
		
		items = base.find_all(class_="storeWrap")

		locator_domain = "swatch.com"

		for item in items:

			location_name = item.find(class_="fn org").text.replace("\n"," ").encode("ascii", "replace").decode().replace("?","e").strip()
			location_name = (re.sub(' +', ' ', location_name)).strip()
			
			streets = item.find_all(class_="street-address")
			if len(streets) == 1:
				street_address = item.find(class_="street-address").text.replace("(Stephen'S Walk)","").encode("ascii", "replace").decode().replace("?","e").strip()
			else:
				street_address = (streets[0].text + " " + streets[1].text).replace("\n","")
			street_address = (re.sub(' +', ' ', street_address)).strip()
			city = item.find(class_="locality").text.encode("ascii", "replace").decode().replace("?","e").strip()
			state = item.find(class_="region").text.encode("ascii", "replace").decode().replace("?","e").strip()
			zip_code = item.find(class_="postal-code").text.replace("CA 94128","94128").strip()
			if not zip_code:
				zip_code = "<MISSING>"
			if len(zip_code.split()) == 3:
				zip_code = zip_code[-7:].strip()
			country_code = codes[i].upper()
			store_number = item.find(class_="storeid")["value"]
			location_type = item.h4.text.strip()
			latitude = item.find(class_="latitude")["value"]
			longitude = item.find(class_="longitude")["value"]
			
			link = "https://www.swatch.com" + item.find(class_="textlink")["href"]
			phone = "<MISSING>"
			hours_of_operation = "<MISSING>"
			if link != "https://www.swatch.com":
				req = session.get(link, headers = HEADERS)
				base = BeautifulSoup(req.text,"lxml")
				
				try:
					phone = base.find(class_="phone").text.strip()
					if phone == "+1 703 720121":
						phone = "<MISSING>"
				except:
					pass
				try:
					hours = base.find_all(class_="opening")
					if len(hours) == 1:
						hours_of_operation = " ".join(list(base.find(class_="opening").span.stripped_strings))
					else:
						hours_of_operation = " ".join(list(hours[0].span.stripped_strings)) + " " + hours[1].text.replace("\n", " ").strip()
						hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
				except:
					pass
			else:
				link = "<MISSING>"

			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
