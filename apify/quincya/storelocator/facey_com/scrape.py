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
	
	base_link = "https://www.facey.com/location-directory"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	locator_domain = "facey.com"

	types = base.find(placeholder="Select a location type").find_all("option")[1:]

	for raw_type in types:

		location_type = raw_type.text.replace("  "," ")
		link_id = raw_type["value"]

		for page_num in range(1,10):
			link = "https://www.facey.com/location-directory/search-results?type=" + link_id + "&page=%s" %page_num

			req = session.get(link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")

			items = base.find_all(class_="col-sm-12")
			
			if len(items) == 0:
				break

			for item in items:

				location_name = item.a.text.encode("ascii", "replace").decode().replace("?","n").strip()
				
				raw_address = list(item.div.div.stripped_strings)

				street_address = raw_address[0].strip()
				city = raw_address[1].split(",")[0].encode("ascii", "replace").decode().replace("?","n").strip()
				state = raw_address[1].split(",")[1].strip()[:-6].strip()
				zip_code = raw_address[1].split(",")[1][-6:].strip()
				country_code = "US"
				store_number = "<MISSING>"
				phone = item.find(class_="locations-listing-phones").a.text
				
				try:
					geo = item.find(class_="locations-listing-maplink").a["href"].split("=")[1].split(",")
					latitude = geo[0]
					longitude = geo[1]
				except:
					latitude = "<MISSING>"
					longitude = "<MISSING>"

				final_link = "https://www.facey.com" + item.a["href"]

				req = session.get(final_link, headers = HEADERS)
				base = BeautifulSoup(req.text,"lxml")

				try:
					hours_of_operation = " ".join(list(base.find(id="psjh_body_2_psjh_twocol_cellone_0_locationHoursContainer").stripped_strings)).replace("\r\n"," ").replace("Hours:","").strip()					
				except:
					try:
						hours_of_operation = " ".join(list(base.find(id="psjh_body_2_psjh_twocol_celltwo_0_locationHoursContainer").stripped_strings)).replace("\r\n"," ").replace("Hours:","").strip()
					except:
						try:
							hours_of_operation = str(base.find(class_="col-xs-12 col-md-8").p).split("/>")[-1].strip().replace("\xa0","").split("\n")[0]
						except:
							hours_of_operation = "<MISSING>"
				hours_of_operation = hours_of_operation.split("PLEASE")[0].split("Website")[0].split("Special")[0].split("Lab")[0].strip()
				
				if "<p>" in hours_of_operation:
					hours_of_operation = "<MISSING>"

				data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
