from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
import re
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="checkngo.com")


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

	states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
			"HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
			"MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
			"NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
			"SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

	data = []
	locator_domain = "checkngo.com"
	
	for state in states:
		log.info("Checking State: " + state)
		base_link = 'https://locations.checkngo.com/service/location/getlocationsin?state='+state+'&brandFilter=Check%20`n%20Go'
		req = session.get(base_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		stores = json.loads(base.text.strip())

		for store in stores:
			location_name = store["StoreName"]
			street_address = (store["Address1"] + " " + store["Address2"]).strip()
			city = store['City']
			state = store["State"]["Code"]
			zip_code = store["ZipCode"]
			country_code = "US"
			store_number = store["StoreNum"]
			location_type = "<MISSING>"
			phone = store['FormattedPhone']

			hours_of_operation = ("Monday " + store["MondayOpen"] + "-" + store["MondayClose"] + " Tuesday " + store["TuesdayOpen"] + "-" + store["TuesdayClose"] + " Wednesday " + store["WednesdayOpen"] + "-" + \
			store["WednesdayClose"] + " Thursday " + store["ThursdayOpen"] + "-" + store["ThursdayClose"] + " Friday " + store["FridayOpen"] + "-" + store["FridayClose"]).strip()
			
			try:
				 weekend = " Saturday " + store["SaturdayOpen"] + "-" + store["SaturdayClose"] + " Sunday " + store["SundayOpen"] + "-" + store["SundayClose"]
				 hours_of_operation = hours_of_operation + weekend
			except:
				pass

			latitude = store['Latitude']
			longitude = store['Longitude']
			link = "https://locations.checkngo.com/locations" + store["Url"]

			# Store data
			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
