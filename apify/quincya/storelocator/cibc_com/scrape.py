from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cibc_com')


def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	found = []
	locator_domain = "cibc.com"

	provs = ["AB", "BC", "SK", "NS", "MB", "QC", "ON", "NT", "PE", "NL", "NU", "YT"]

	for prov in provs:
		logger.info(prov)
		for num in range(1,50):
			base_link = "https://locations.cibc.com/search/%s/?t=&q=%s&page=%s&filters=filter-_-Branch" %(prov.lower(),prov,num)
			
			req = session.get(base_link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")

			items = base.find(id="results_list").find_all("li")

			all_scripts = base.find_all('script')
			for script in all_scripts:
				if '"lat":' in str(script):
					script = script.text
					break
			lats = re.findall(r'lat":[0-9]{2}\.[0-9]+',script)
			lons = re.findall(r'lon":-[0-9]{2,3}\.[0-9]+',script)
			ids = re.findall(r'"id":"[0-9]+',script)

			for i, item in enumerate(items):
				store_number = ids[i].split('"')[-1]
				if store_number in found:
					continue
				found.append(store_number)
				
				location_name = item.h2.text.strip()
				if not location_name:
					continue
				street_address = item.find(class_="line street-address").text.strip()
				city = item.find(class_="locality").text.strip()
				state = item.find(class_="region").text.strip()
				zip_code = item.find(class_="postal-code").text.strip()
				country_code = "CA"
				location_type = "<MISSING>"
				phone = item.find(class_="tel").text.strip()

				if "temporary clos" in item.text.lower():
					hours_of_operation = "Temporary Closure"
				else:
					try:
						hours_of_operation = " ".join(list(item.find(class_="locationHours bankHours").table.stripped_strings))
					except:
						hours_of_operation = "<MISSING>"

				latitude = lats[i].split(":")[-1]
				longitude = lons[i].split(":")[-1]

				link = "https://locations.cibc.com" + item.a["href"]

				data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

			if not base.find('a', attrs={'aria-label': "Next page"}):
				break

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
