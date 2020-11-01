from sgrequests import SgRequests
import csv

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

	locator_domain = "mazdausa.com"

	data = []
	found_poi = []

	for i in range(50):
		base_link = "https://www.mazdausa.com/handlers/dealer.ajax?dealerName=%&p=" + str(i)
		
		stores = session.get(base_link,headers=HEADERS).json()["body"]["results"]

		if len(stores) == 0:
			break

		for store in stores:

			id_ = store['id']
			if id_ not in found_poi:
				found_poi.append(id_)
			else:
				continue

			location_name = store['name']
			try:
				street_address = store['address1'] + " " + store['address2']
			except:
				street_address = store['address1']

			city = store['city']
			state = store['state']
			zip_code = store['zip']

			if street_address == "ROUTE 30 EAST":
				street_address = "5110 ROUTE 30 EAST"
			if street_address == "U.S. 460 BUSINESS":
				street_address = "125 Jennelle Rd".upper()
				city = "Christiansburg".upper()
				zip_code = "24073"

			country_code = "US"
			store_number = store['id']
			location_type = "<MISSING>"
			phone = store['dayPhone']

			hours_of_operation = "<MISSING>"

			latitude = store['lat']
			longitude = store['long']

			link = store["webUrl"]
			if not link:
				link = "<MISSING>"

			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
