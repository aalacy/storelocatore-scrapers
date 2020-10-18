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
	
	base_link = "https://www.brownbear.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all(class_="street")
	locator_domain = "brownbear.com"

	for item in items:
		link = "https://www.brownbear.com" + item.a['href']

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.h1.text.strip()

		street_address = location_name[location_name.find("-")+1:location_name.rfind("(")].strip()
		city = location_name.split("-")[0].strip()
		state = base.find('meta', attrs={'name': 'description'})['content'].split(",")[-1].split()[0].strip()
		zip_code = base.find('meta', attrs={'name': 'description'})['content'].split(",")[-1].split()[1].strip()
		if street_address == "8296 Avondale Way NE":
			state = "Washington"
			zip_code = "98052"
		country_code = "US"
		store_number = link.split("-")[-1]
		location_type = location_name.split("(")[-1].split(")")[0].strip()
		phone = base.find(class_="panel-body").find_all('p')[-1].text.split("Phone Number")[-1]
		hours_of_operation = base.find_all(class_="panel-body")[1].find(class_="col-md-6").text.replace("\n"," ").split("Hours")[-1].strip()

		map_link = base.iframe['src'].replace("\n","")
		req = session.get(map_link, headers = HEADERS)
		map_str = str(BeautifulSoup(req.text,"lxml"))
		geo = re.findall(r'\[[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\]', map_str)[0].replace("[","").replace("]","").split(",")
		latitude = geo[0]
		longitude = geo[1]
		if street_address == "2421 148th Ave NE":
			latitude = "47.6318474"
			longitude = "-122.1458327"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
