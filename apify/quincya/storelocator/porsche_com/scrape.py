from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="porsche.com")


def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_links = ["https://www.porsche.com/all/dealer2/GetLocationsWebService.asmx/GetLocationsInStateSpecialJS?market=usa&siteId=usa&language=none&state=&_locationType=Search.LocationTypes.Dealer&searchMode=proximity&searchKey=43.1758248%7C-76.07399989999999&address=76107&maxproximity=10000&maxnumtries=&maxresults=1000",
				"https://www.porsche.com/all/dealer2/GetLocationsWebService.asmx/GetLocationsInStateSpecialJS?market=canada&siteId=canada&language=en&state=&_locationType=Search.LocationTypes.Dealer&searchMode=proximity&searchKey=52.088165%7C-106.6498956&address=S7J%205L6,%20ca&maxproximity=10000&maxnumtries=&maxresults=1000"]

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	data = []

	for base_link in base_links:
		req = session.get(base_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		
		items = base.find("listoflocations").find_all("location")

		locator_domain = "porsche.com"
		log.info("Getting POIs..Could take up to an hour ..")
		for item in items:
			location_name = item.find("name").text.encode("ascii", "replace").decode().replace("?","e")
			street_address = item.find("street").text.replace("Côte","Cote")
			city = item.find("city").text.encode("ascii", "replace").decode().replace("?","e")
			state = item.find("statecode").text.upper()
			zip_code = item.find("postcode").text
			if len(zip_code) == 4:
				zip_code = "0" + zip_code
			store_number = item.find("id").text
			location_type = "<MISSING>"
			latitude = item.find("coordinates").find("lat").text
			longitude = item.find("coordinates").find("lng").text.replace("E+07","")
			#phone = item.find("phone").text
			hours_of_operation = "<INACCESSIBLE>"

			if "canada" in base_link:
				country_code = "CA"
			else:
				country_code = "US"

			link = item.find("url1").text
			# print(link)

			try:
				req = session.get(link, headers = HEADERS)
				base = BeautifulSoup(req.text,"lxml")
				try:
					phone = re.findall("[[(\d)]{3}\.[\d]{3}\.[\d]{4}", str(base))[0]
				except:
					try:
						phone = re.findall("[[(\d)]{3}-[\d]{3}-[\d]{4}", str(base))[-1]
					except:
						try:
							phone = re.findall("\([\d]{3}\) [\d]{3}-[\d]{4}", str(base))[0]
						except:
							phone = "<MISSING>"
			except:
				phone = item.find("phone").text
				link = "<MISSING>"

			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
