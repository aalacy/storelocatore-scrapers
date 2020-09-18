import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "http://camillescafe.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)

	base = BeautifulSoup(req.text,"lxml")
	state_links = re.findall(r'\/state\/[a-z]{2}\/', base.text.lower())

	data = []
	all_links = []
	locator_domain = "camillescafe.com"

	for state_link in state_links:
		state_link = "http://camillescafe.com" + state_link
		req = session.get(state_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		links = base.find_all(class_="location-title")
		for i in links:
			all_links.append(i.a["href"])

	for link in all_links:
		if "coming-soon" in link:
			continue

		print(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		loc = base.h2.text.strip()
		location_name = loc[:loc.find("\t")].replace("–","-").strip()
		phone = base.find(class_="company_info").find_all("p")[2].text.replace("Phone:","").strip()
		if not phone:
			phone = "<MISSING>"
		hours = base.find(class_="company_info").find_all("p")[1].text.replace("Hours:","").strip()
		hours_of_operation = (re.sub(' +', ' ', hours)).strip()
		if len(hours_of_operation) < 5:
			hours_of_operation = "<MISSING>"

		country_code = 'US'
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		all_scripts = base.find_all('script')
		fin_script = ""
		for script in all_scripts:
			if "lng" in str(script):
				script = script.text.replace('\n', '').strip()
				fin_script = script[script.find("=")+1:script.rfind("};")+1].strip()
				break

		if fin_script:
			store = json.loads(fin_script)['pois'][0]
			latitude = store["point"]["lat"]
			longitude = store["point"]["lng"]
			raw_address = store['address'].split(",")
			try:
				street_address = raw_address[0].strip()
				city = raw_address[-3].strip()
				state = raw_address[-2].split()[0].strip()
				zip_code = raw_address[-2].split()[1].strip()
			except:
				raw_address = str(base.find(class_="company_info").p).replace("Mayaguez"," Mayaguez").split("</span>")[1].split("  ")
				street_address = raw_address[0]
				city_line = raw_address[1].replace("</p>","").replace("Caribbean",",Caribbean").strip().split(",")
				city = city_line[-2].strip()
				state = city_line[-1][:-6].strip()
				zip_code = city_line[-1][-6:].strip()
		else:
			raw_address = base.find(class_="company_info").p.text.replace("Address:","").strip().split()
			if raw_address[-1].isnumeric():
				zip_code = raw_address[-1].strip()
				street_address = " ".join(raw_address[:-3])
				city = raw_address[-3].replace(",","").strip()
				state = raw_address[-2].split()[0].strip()
			else:
				zip_code = "<MISSING>"
				street_address = " ".join(raw_address[:-2])
				city = raw_address[-2].replace(",","").strip()
				state = raw_address[-1].split()[0].strip()

			latitude = "<MISSING>"
			longitude = "<MISSING>"

		if "Expreso de" in city:
			street_address = street_address + " " + "Expreso de Diego #9"
			city = "Bayamon"
			state = "Puerto Rico"
			zip_code = "<MISSING>"

		if street_address == "Dos Bocas":
			street_address = "Plaza Encantada Local C-1 Intersection of Avenida Encantada and State Road 181 Barrio Dos Bocas"
			city = "Trujillo Alto"
			state = "Puerto Rico"
			zip_code = "00976"

		if "Canoga" in street_address:
			street_address = street_address.replace("Canoga","").strip()
			city = "Canoga Park"

		if city == "Louis":
			city = "St. Louis"
			street_address = street_address.replace("St.","").strip()

		# Store data
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
