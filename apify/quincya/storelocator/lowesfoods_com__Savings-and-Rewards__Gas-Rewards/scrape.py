from sgrequests import SgRequests
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
	
	base_link = "https://www.lowesfoods.com/StoreLocator/SearchNearByStores"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	payload = {'Radius': '1000',
			'HasFuelStation': 'true',
			'SearchByRadius': 'true'}

	stores = session.post(base_link,headers=HEADERS,data=payload).json()

	data = []
	locator_domain = "lowesfoods.com"

	for store in stores:
		location_name = store["StoreName"]
		street_address = (store["Address1"] + " " + store["Address2"]).strip()
		city = store['City']
		state = store["State"]
		zip_code = store["Zipcode"]
		country_code = "US"
		store_number = store["StoreNumber"]
		location_type = "<MISSING>"
		phone = store['Phone']
		hours_of_operation = store["StoreOpenHours"].replace("<br>"," ").strip()
		latitude = store['Latitude']
		longitude = store['Longitude']
		link = "https://www.lowesfoods.com" + store["PageUrl"]

		# Store data
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
