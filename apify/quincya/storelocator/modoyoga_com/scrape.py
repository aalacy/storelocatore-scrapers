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
	
	base_link = "https://modoyoga.com/search-results/?userLocation="

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	all_links = []
	found_poi = []

	raw_data = str(base.find(class_="acf-map acf-map-height"))
	items = raw_data.split('<div class="marker" ')[1:]

	locator_domain = "modoyoga.com"

	for item_str in items:
		if "Canada" in item_str:
			country_code = "CA"
		elif "USA" in item_str:
			country_code = "US"
		else:
			country_code = "NA"

		try:
			link = "http" + item_str.split("http")[-1].split('"')[0]
		except:
			continue

		if link not in found_poi:
			all_links.append([country_code,link])
			found_poi.append(link)

	for row in all_links:
		country_code = row[0]
		link = row[1]
		if "/paris" in link or "/janob" in link:
			continue

		# print(link)
		req = session.get(link, headers = HEADERS)

		base = BeautifulSoup(req.text,"lxml")
		locs = base.find_all(class_="container location-info")

		for loc in locs:
			if "Our final chapter" in base.text:
				continue

			if len(locs) == 1:
				location_name = base.find(class_="header-logo").text.encode("ascii", "replace").decode().replace("?","e").strip()
			else:
				location_name = loc.h2.text.encode("ascii", "replace").decode().replace("?","e").strip()

			if "Virtual" in location_name:
				continue

			raw_address = loc.p.text.replace("Milton ON","Milton, ON").replace("Catharines ON","Catharines, ON").replace("\r\nCanada","").split("\r\n")

			if len(raw_address) > 1 and len(raw_address[-1]) > 40:
				raw_address.pop(-1)

			if "door code" in raw_address[-1] or "Text Us" in raw_address[-1]:
				raw_address.pop(-1)

			if len(raw_address) == 1:
				raw_address = raw_address[0].split(",")
				street_address = raw_address[0].strip()
				if "3252-B W Lake Street" in street_address:
					street_address = street_address + " suite b"
					city = "Minneapolis"
					state = "MN"
					zip_code = "55416"
				else:
					city = raw_address[1].strip()
					state = raw_address[2].strip()[:2]
					zip_code = raw_address[2].strip()[2:].strip()
			elif len(raw_address) == 2:
				street_address = raw_address[0].strip()
				if "4701 Hastings St, Burnaby" in street_address:
					street_address = "4701 Hastings St"
					city = "Burnaby"
					state = "BC"
					zip_code = "V5C 2K8"
				elif "677 Richmond Street" in street_address:
					city = "London"
					state = "ON"
					zip_code = "N6A 5M1"
				elif "425 Southdale Road" in street_address:
					city = "London"
					state = "ON"
					zip_code = "N6P 1M7"
				else:
					city = raw_address[-1].split(",")[0].strip()
					state = raw_address[-1].split(",")[1].split()[0].strip()
					zip_code = raw_address[-1].split(",")[1].replace(state,"").strip()
			elif len(raw_address) > 2:
				if len(raw_address[-1].replace(".","").strip()) < 8:
					city_line = -2
					zip_code = raw_address[-1].replace(".","").strip()
					city = raw_address[city_line].split(",")[0].strip()
					try:
						state = raw_address[city_line].split(",")[1].replace(".","").strip()
					except:
						if city == "Sherwood Park":
							state = zip_code
							zip_code = "<MISSING>"
				else:
					city_line = -1
					city = raw_address[city_line].split(",")[0].strip()
					state = raw_address[city_line].split(",")[1].split()[0].strip()
					try:
						zip_code = raw_address[city_line].split(",")[1].split()[1].strip()
					except:
						zip_code = ""
				street_address = " ".join(raw_address[:city_line])

			street_address = street_address.replace("(upstairs)","").replace("  "," ").strip()
			if street_address[-1:] == ",":
				street_address = street_address[:-1]

			digit = re.search("\d", street_address).start(0)
			if digit != 0:
				street_address = street_address[digit:]

			city = city.encode("ascii", "replace").decode().replace("?","e")

			if state.upper() == "BRITISH":
				state = "British Columbia"
				zip_code = ""

			try:
				phone = loc.find_all("p")[2].text.split("\n")[0].replace("YOGA","9642").replace("tx us","").strip()
			except:
				phone = "<MISSING>"

			store_number = "<MISSING>"
			location_type = "<MISSING>"

			if "TEMPORARY CLOSURE" in base.text.upper() and len(locs) == 1:
				hours_of_operation = "Temporarily Closed"
			elif "temporarily closed" in base.text.lower() and len(locs) == 1:
				hours_of_operation = "Temporarily Closed"
			else:
				hours_of_operation = loc.find_all("p")[-1].text.replace("PM","pm").replace("AM","am").replace("a.m.","am").replace("p.m.","pm").replace("\r\n","").replace("pm","pm ").split("\n")[0]
				if "pm" not in hours_of_operation and "Monday" not in hours_of_operation or "parking" in hours_of_operation.lower():
					hours_of_operation = loc.find_all("p")[-2].text.replace("PM","pm").replace("AM","am").replace("a.m.","am").replace("p.m.","pm").replace("\r\n","").replace("pm","pm ").split("\n")[0]
					if "pm" not in hours_of_operation:
						hours_of_operation = loc.find_all("p")[-2].text.replace("PM","pm").replace("AM","am").replace("a.m.","am").replace("p.m.","pm").replace("\r\n","").replace("pm","pm ")
						hours_of_operation = hours_of_operation[hours_of_operation.find("Mon"):hours_of_operation.rfind("pm")+2]
				
				if "pm" not in hours_of_operation and "Monday" not in hours_of_operation:
					hours_of_operation = "<MISSING>"
			hours_of_operation = hours_of_operation.replace("day","day ").replace("Sat"," Sat").replace("Sun"," Sun").encode("ascii", "replace").decode().replace("?","-")
			hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
			if "Mon" in hours_of_operation:
				hours_of_operation = hours_of_operation[hours_of_operation.find("Mon"):]

			if "pm" in hours_of_operation and hours_of_operation[-2:] != "am":
				hours_of_operation = hours_of_operation[:hours_of_operation.rfind("pm")+2]

			hours_of_operation = hours_of_operation.split("Text")[0].strip()
			hours_of_operation = hours_of_operation.split("times:")[-1]

			map_link = loc.iframe["src"]
			req = session.get(map_link, headers = HEADERS)
			map_str = BeautifulSoup(req.text,"lxml")
			geo = re.findall(r'\[[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\]', str(map_str))[0].replace("[","").replace("]","").split(",")
			latitude = geo[0]
			longitude = geo[1]
				
			if len(zip_code) < 4:
				zip_code = re.findall(r', .+, Canada', str(map_str))[0].split(", Canada")[0].strip()[-7:]

			if country_code == "NA":
				if " " in zip_code:
					country_code = "CA"
				elif len(zip_code) == 5:
					country_code = "US"

			data.append([locator_domain, link, location_name, street_address, city, state.upper(), zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
