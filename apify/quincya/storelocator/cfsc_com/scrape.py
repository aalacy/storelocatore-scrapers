from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import sgzip
import json
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="cfsc.com")

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

	found_poi = []
	data = []

	zips = sgzip.for_radius(50)
	log.info("Checking " + str(len(zips)) + " zipcodes. Can take up to an hour ..")
	for i, zip_code in enumerate(zips):
		# print("Zip %s of %s" %(i+1,len(zips)))
		link = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=100&location=%s&limit=50&api_key=7620f61553e8f9aac3c03e159d2d8072&v=20181201&resolvePlaceholders=true&entityTypes=location" %zip_code
		
		req = session.get(link, headers = HEADERS)
		try:
			base = BeautifulSoup(req.text,"lxml")
			# print(zip_code)
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		store_data = json.loads(base.text)['response']['entities']
		locator_domain = "cfsc.com"

		for store in store_data:

			page_url = store["landingPageUrl"]
			if page_url not in found_poi:
				found_poi.append(page_url)
			else:
				continue

			location_name = store["name"]
			# print(location_name)

			street_address = store["address"]["line1"]
			city = store["address"]["city"]
			state = store["address"]["region"]
			zip_code = store["address"]["postalCode"]
			country_code = store["address"]["countryCode"]
			store_number = page_url.split("-")[-1]
			try:
				location_type = ','.join(store["services"])
			except:
				location_type = "<MISSING>"
			phone = store["mainPhone"]
			try:
				raw_hours = store["hours"]
				hours_of_operation = ""
				for raw_hour in raw_hours:
					try:
						end = raw_hours[raw_hour]["openIntervals"][0]["end"]
						start = raw_hours[raw_hour]["openIntervals"][0]["start"]
						hours_of_operation = (hours_of_operation + " " + raw_hour + " " + start + "-" + end).strip()
					except:
						hours_of_operation = (hours_of_operation + " " + raw_hour + " Closed").strip()
			except:
				hours_of_operation = "<MISSING>"

			try:
				geo = store["geocodedCoordinate"]
			except:
				geo = store["yextDisplayCoordinate"]
			latitude = geo["latitude"]
			longitude = geo["longitude"]
			
			data.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
				
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
