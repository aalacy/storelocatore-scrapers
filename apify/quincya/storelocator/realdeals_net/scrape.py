from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
import json
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="realdeals.net")


def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://realdeals.net/find-a-store/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	text = base.find(class_="fusion-column-wrapper").text
	all_links = re.findall(r'http://realdeals.net/[a-z]+', text)
	locator_domain = "realdeals.net"

	data = []
	for i, link in enumerate(all_links):
		log.info(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		try:
			raw_data = base.find(id="front-address").find(id="text-4").text.replace("Get Directions","").replace(", Canada |","").replace("Canada","")\
			.replace("Ankeny"," | Ankeny").replace("Dr Cedar","Dr | Cedar").replace("Street, ","Street | ").replace("\r\n"," | ")\
			.replace("| 307)","| (307)").replace("St, Spanish","St | Spanish").replace("Kearney, Nebraska","Kearney | Nebraska").replace(" B,"," B |")\
			.replace(" C,"," C |").replace("NW Rochester","NW | Rochester").replace(" 1, "," 1 | ").replace("102 Powell","102 | Powell").replace("Ave Butte","Ave | Butte")\
			.replace("Ave La","Ave | La").replace("V1Y-9T1","V1Y 9T1").replace("Dr Cedar","Dr | Cedar").strip().split("|")
			location_name = base.h3.text.strip()
			if location_name.upper() == "REGINA REAL DEALS":
				location_name = "Regina, Saskatchewan"
			phone = raw_data[2].strip()
			if not phone:
				phone = "<MISSING>"
			hours_of_operation = base.find(id="front-hours").div.text.replace("\r\n"," ").replace("\n"," ").replace("–","-").replace("Shop Online!","")
			if not hours_of_operation:
				hours_of_operation = base.find(id="front-hours").find_all("div")[1].text.replace("\r\n"," ").replace("\n"," ").replace("–","-").replace("Shop Online!","")
			hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
			store = json.loads(base.find(id="wpgmza_map")["data-settings"])
			latitude = store['map_start_lat']
			longitude = store['map_start_lng']
		except:
			try:
				raw_data = base.find_all("h4")[1].text.replace("\xa0","").split("\n")
				location_name = base.h2.text.strip()
				phone = "<MISSING>"
				hours_of_operation = base.h4.text.replace("\n", " ").strip()
				map_link = base.find(class_="fusion-button button-flat fusion-button-round button-large button-default button-1")['href']
				at_pos = map_link.rfind("@")
				latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
				longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
			except:
				try:
					raw_data = base.find_all(class_="fusion-text")[4].p.text.replace("\xa0","").split("\n")
					location_name = base.h1.text.strip()
					phone = base.find_all(class_="fusion-text")[5].p.a.text.replace("\n", " ").strip()
					hours_of_operation = base.find_all(class_="fusion-text")[3].text.replace("\n", " ").strip()
					script = base.text
					lat_pos = script.find('latitude') + 11
					latitude = script[lat_pos:script.find(',',lat_pos)-1]
					long_pos = script.find('longitude') + 12
					longitude = script[long_pos:script.find(',',long_pos)-3]
				except:
					continue

		if longitude == "240.594345":
			longitude = "-119.405655"

		street_address = raw_data[0].replace("Cedar Falls, IA","").replace("Kearney","").strip()
		city = location_name.split(",")[0].strip()
		state = location_name.split(",")[1].strip()
		location_name = "Real Deals on Home Decor - " + location_name
		zip_code = raw_data[1][-7:].strip()
		if "Suite" in zip_code:
			street_address = street_address + " " + zip_code
			zip_code = raw_data[2][-7:].strip()
		country_code = "US"
		if "," in zip_code or zip_code == "ter VA":
			zip_code = "<MISSING>"
		if " " in zip_code:
			if zip_code[-5:].isnumeric():
				zip_code = zip_code[-5:]
			else:
				zip_code = raw_data[1][-8:].strip()
				country_code = "CA"
		if not zip_code:
			zip_code = "<MISSING>"
		if zip_code == "T6A OH9":
			zip_code = "T5H 2T2"
		location_type = "<MISSING>"
		store_number = "<MISSING>"
		hours_of_operation = hours_of_operation.replace("SHOP ONLINE!","").replace("!","").replace("HOURS:","").strip()

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
