from sgrequests import SgRequests
import csv

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = 'https://www.copart.com/public/data/locations/retrieveLocationsList?continentCode=NORTH_AMERICA'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	store_data = session.get(base_link, headers = HEADERS).json()["data"]["countries"]

	data = []
	locator_domain = "copart.com"

	for country in store_data:
		stores = store_data[country]

		for store in stores:
			location_name = store['yardName']
			street_address = (store['yardAddress1'] + " " + store['yardAddress2']).strip()
			city = store['yardCity']
			state = store['yardStateCode']
			zip_code = store['yardZip']
			country_code = store['yardCountryCode'].replace("USA","US").replace("CAN","CA")
			if country_code == "US":
				zip_code = zip_code.replace(" ","-")
			store_number = store['yardNumber']
			location_type = "<MISSING>"
			phone = store['yardPhoneAreaCode'] + store['yardPhoneNumber']
			hours_of_operation = store['yardDays'].replace("through","To") + " " + store['yardHours']
			latitude = store['yardLatitude']
			longitude = store['yardLongitude']
			if latitude == 0:				
				latitude = "<MISSING>"
				longitude = "<MISSING>"
			link = "https://www.copart.com" + store['locationUrl']

			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
