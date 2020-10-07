from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
import re
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="prada.com")

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.prada.com/us/en/store-locator.html"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all(class_="d-none")[-1].find_all("a")
	locator_domain = "prada.com"

	for item in items:
		link = item["href"]
		if "china" in link or "australia" in link or "dubai" in link or "shinjuku" in link:
			continue

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		js = base.find(id="jsonldLocalBusiness").text
		try:
			store = json.loads(js)
		except:
			continue		

		country_code = store['address']['addressCountry']
		if country_code not in ["US","CA"]:
			continue
		log.info(link)
		location_name = store['name'].encode("ascii", "replace").decode().replace("?","e")
		street_address = store['address']['streetAddress'].replace("Bal Harbour FL 33154","").replace("W. Montreal, QC H3G 1P7","").replace("New York City, New York 10022","").strip().replace("  "," ")
		city = store['address']['addressLocality']
		state = "<MISSING>"
		zip_code = store['address']['postalCode']
		store_number = link.split(".")[-2]
		location_type = "<MISSING>"
		phone = store['telephone'].encode("ascii", "replace").decode().replace("?","")
		hours_of_operation = store['openingHours'].strip().replace("  "," ").replace("--","Closed")
		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
