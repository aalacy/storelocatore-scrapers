from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re
from random import randint


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.porsche-design.us/us/en/storelocator/Search/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	all_links = []
	data = []

	us_states_codes = ['AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MH', 'MA', 'MI', 'FM', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PW', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'VI', 'WA', 'WV', 'WI', 'WY']
	
	for state in us_states_codes:
		print("Searching: " + state)
		# Request post
		payload = {'Country': 'US',
				'ZipOrLocus': state,
				'Distance': '300'}

		response = session.post(base_link,headers=HEADERS,data=payload)
		time.sleep(randint(2,4))
		base = BeautifulSoup(response.text,"lxml")

		try:
			items = base.find(class_="col-sm-12 col-md-6").find_all(class_="store-search-result-container d-flex")
		except:
			continue
		for item in items:
			location_name = item.find(class_="h5").text
			link = "https://www.porsche-design.us" + item.find(class_="text-uppercase more-link")['href']
			if link not in all_links:
				all_links.append(link)

	total_links = len(all_links)
	for i, link in enumerate(all_links):
		# print("Link %s of %s" %(i+1,total_links))
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		locator_domain = "porsche-design.us"
		location_type = "<MISSING>"

		item = base.find(class_="container mt-5")
		location_name = item.find('h1').text.strip()
		if "Santa Fe" in location_name:
			continue
		print(link)

		latitude = "<MISSING>"
		longitude = "<MISSING>"
		all_scripts = base.find_all('script')
		for script in all_scripts:
			if "lng" in str(script):
				script = str(script)
				coords = re.findall(r'\[-.+,.+\]},', script)[0]
				latitude = coords.split(",")[1][:-2]
				longitude = coords.split(",")[0][1:]
				break
		raw_street = re.findall(r'"street":.+","phoneNum', script)[0]
		street_address = raw_street.split(":")[-1][1:-13]
		if len(street_address) < 5:
			continue
		if street_address == "Oakbrook Center, 69 Oakbrook Center":
			city = "Oak Brook"
			state = "IL"
			zip_code = "60523"
		elif street_address == "Interanational Airport JFK":
			city = "Jamaica"
			state = "NY"
			zip_code = "11430"
		elif street_address == "520 N Michigan Ave":
			city = "Chicago"
			state = "IL"
			zip_code = "60611"
		else:
			try:
				raw_city = re.findall(r'"city":"[a-zA-Z]+"', script)[0]
				bad = False
			except:
				bad = True
			if not bad:
				city = raw_city.split(":")[-1].replace('"',"")
				raw_zip = re.findall(r'"zip":.+"street"', script)[0]
				state = raw_zip.split(":")[-1].split(",")[0].replace('"',"").split()[0]
				if state.isnumeric():
					zip_code = state
					state = "<MISSING>"
				else:
					try:
						zip_code = raw_zip.split(":")[-1].split(",")[0].replace('"',"").split()[1]
					except:
						zip_code = "<MISSING>"
			else:
				try:
					raw_city = re.findall(r'"zip":.+"street"', script)[0]
					city = raw_city.split(":")[-1].split(",")[0].replace('"',"").split()[0]
					raw_zip = re.findall(r'"city":.+"zip"', script)[0]
					state = raw_zip.split(":")[-1].split(",")[0].replace('"',"").split()[0]
					if state.isnumeric():
						zip_code = state
						state = "<MISSING>"
					else:
						try:
							zip_code = raw_zip.split(":")[-1].split(",")[0].replace('"',"").split()[1]
						except:
							zip_code = "<MISSING>"
				except:
					raw_address = str(item.p)[3:].replace("</p>","").replace("\n","").strip().split("<br/>")

					street_address = raw_address[0].strip()
					if street_address[-1:] == ",":
						street_address = street_address[:-1].strip()
					try:
						city_line = raw_address[1].strip().split(",")
						city = city_line[0].strip()
						state = city_line[-1].strip().split()[0].strip()
						zip_code = city_line[-1].strip().split()[1].strip()
					except:
						street_address = "<MISSING>"
						if location_name == "JFK Airport":
							state = "NY"
							city = "NY"
						else:
							state = "<MISSING>"
							city = "<MISSING>"
		if street_address[-1:] == ",":
			street_address = street_address[:-1]

		if state == "Las":
			state = "NV"
			city = "Las Vegas"
			raw_zip = re.findall(r'"zip":.+"street"', script)[0]
			state = raw_zip.split(":")[-1].split(",")[0].replace('"',"").split()[0]
			if state.isnumeric():
				zip_code = state
				state = "<MISSING>"
			else:
				try:
					zip_code = raw_zip.split(":")[-1].split(",")[0].replace('"',"").split()[1]
				except:
					zip_code = "<MISSING>"
		if state == "Boca":
			state = "FL"
			city = "Boca Raton"
			zip_code = "33431"

		country_code = "US"

		if len(zip_code) == 3:
			raw_address = str(item.p)[3:].replace("</p>","").replace("\n","").strip().split("<br/>")
			city_line = raw_address[1].strip().split(",")
			zip_code = " ".join(city_line[-1].strip().split()[-2:])
			country_code = "CA"

		raw_phone = re.findall(r'"phoneNumber":".+,"email', script)[0]
		phone = raw_phone.split(":")[-1].replace('"',"")[:-6]
		phone = phone.replace("001- ","").strip()

		# raw_phone = item.find_all("p")[1].text.replace("\n","")
		# phone = re.findall(r'\+.+ E', raw_phone)[0][:-1].strip()
		
		store_number = "<MISSING>"

		hours_of_operation = ""
		ps = item.find_all(class_="mb-5")
		for p in ps:
			if "hours" in p.text:
				raw_hours = p.text.replace("opening hours","").replace("&amp;","&").replace("\n"," ").strip()
				hours_of_operation = (re.sub(' +', ' ', raw_hours)).strip()
				break
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
