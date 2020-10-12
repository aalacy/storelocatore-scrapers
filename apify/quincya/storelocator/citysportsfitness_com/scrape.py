from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.citysportsfitness.com/Pages/GetClubLocations.aspx/GetClubLocationsByStateAndZipCode"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	js = {'zipCode': '', 'state': "CA"}
	response = session.post(base_link,headers=HEADERS,json=js)
	base = BeautifulSoup(response.text,"lxml")

	stores = json.loads(base.text.strip())['d']

	data = []

	locator_domain = "citysportsfitness.com"

	for store in stores:
		location_name = store['Description']
		raw_address = store['Address'].split("<br />")
		street_address = raw_address[0].strip()
		city_line = raw_address[1].strip().split(",")
		city = store['City']
		state = store['State']
		zip_code = city_line[1].split()[1].strip()
		country_code = "US"
		store_number = store['ClubID']
		location_type = "Club Status " + str(store['ClubStatus'])
		latitude = store['Latitude']
		longitude = store['Longitude']

		link = "https://www.citysportsfitness.com/pages/" + store['ClubHomeURL']
		# print(link)

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		phone = base.find(id="ctl00_MainContent_lblClubPhone").text.strip()
		hours_of_operation = " ".join(list(base.find(id="divClubHourPanel").stripped_strings)).replace("CLUB HOURS","").strip()

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
