import csv
import time
import re
from sgselenium import SgSelenium
import datetime
import sgzip
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="citizensbank.com")

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
		
	driver = SgSelenium().chrome()
	time.sleep(2)

	data = []
	found_poi = []

	date_str = str(datetime.date.today())

	coords = sgzip.coords_for_radius(200)
	for coord in coords:
		lat, lng = coord[0], coord[1]
		base_link = "https://www.citizensbank.com/apps/ApiProxy/BranchlocatorApi/api/BranchLocator?RequestHeader%5BRqStartTime%5D=" + date_str + "&coordinates%5BLatitude%5D=" + lat + "&coordinates%5BLongitude%5D=" + lng + "&searchFilter%5BIncludeAtms%5D=false&searchFilter%5BIncludeBranches%5D=true&searchFilter%5BIncludeVoiceAssistedAtms%5D=false&searchFilter%5BIncludeSuperMarketBranches%5D=true&searchFilter%5BIncludeOpenNow%5D=false&searchFilter%5BRadius%5D=200"
		# print(lat, lng)

		driver.get(base_link)
		time.sleep(8)

		main = driver.find_element_by_tag_name("BranchCollection")
		items = main.find_elements_by_xpath("./*")
		log.info("Getting data ..")
		for item in items:
			
			locator_domain = "citizensbank.com"
			if item.find_element_by_tag_name("IsBranch").get_attribute("innerHTML") == "false":
				continue
			street_address = item.find_element_by_tag_name("StreetAddress").get_attribute("innerHTML").split("[")[-1][:-3].replace("Cambridge MA","").replace("  "," ").strip()
			if street_address[-1:] == ",":
				street_address = street_address[:-1]
			if street_address in found_poi:
				continue
			found_poi.append(street_address)
			location_name = item.find_element_by_tag_name("BranchName").get_attribute("innerHTML").split("[")[-1][:-3]
			# print(location_name)
			city = item.find_element_by_tag_name("City").get_attribute("innerHTML")
			state = item.find_element_by_tag_name("State").get_attribute("innerHTML")
			zip_code = item.find_element_by_tag_name("Zip").get_attribute("innerHTML").replace(".","")
			country_code = "US"
			store_number = item.find_element_by_tag_name("BranchId").get_attribute("innerHTML")
			phone = item.find_element_by_tag_name("Phone").get_attribute("innerHTML")
			location_type = "<MISSING>"
			hours_of_operation = item.find_element_by_tag_name("LobbyHours").find_element_by_tag_name("Description").get_attribute("innerHTML").replace("na","Closed")
			latitude = item.find_element_by_tag_name("Latitude").get_attribute("innerHTML")
			longitude = item.find_element_by_tag_name("Longitude").get_attribute("innerHTML")
			link = "https://www.citizensbank.com/customer-service/branch-locator.aspx"

			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
