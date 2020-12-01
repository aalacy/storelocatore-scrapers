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
	
	base_link = "https://www.carx.com/dnsc/public/ajax/lookupLocationsRadius.php?radius=5000&lat=31.9685988&lng=-99.9018131"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	
	data = []

	locator_domain = "carx.com"

	stores = session.get(base_link, headers = HEADERS).json()

	for store in stores:
		location_name = store['LocationTitle']
		street_address = store['AddressLine1']
		city = store['City']
		state = store['State']
		zip_code = store['Zip']
		country_code = "US"
		store_number = store['locationID']
		location_type = "<MISSING>"
		phone = store['Phone']
		latitude = store['Lat']
		longitude = store['Lng']
		link = "https://www.carx.com" + store['URL']

		hours_of_operation = ""
		for i in range(7):
			day_open = "hours%sopen" %i
			day_close = "hours%sclose" %i
			day_stat = "hours%sisclosed" %i

			if i == 0:
				day = "Sunday"
			elif i == 1:
				day = "Monday"
			elif i == 2:
				day = "Tuesday"
			elif i == 3:
				day = "Wednesday"
			elif i == 4:
				day = "Thursday"
			elif i == 5:
				day = "Friday"
			elif i == 6:
				day = "Saturday"

			if store[day_stat] == 1:
				hours = day + " Closed"
			else:
				hours = day + " " + store[day_open] + "-" + store[day_close]

			hours_of_operation = (hours_of_operation + " " + hours).strip()

			if hours_of_operation == "Sunday Closed Monday Closed Tuesday Closed Wednesday Closed Thursday Closed Friday Closed Saturday Closed":
				hours_of_operation = "Temporarily Closed"
				
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
