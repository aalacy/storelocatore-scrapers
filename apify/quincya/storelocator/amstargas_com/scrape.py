from sgrequests import SgRequests
from bs4 import BeautifulSoup
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
	
	base_link = "https://www.amstargas.com/amstar_locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	all_scripts = base.find_all('script')
	for script in all_scripts:
		if "latlons" in str(script):
			script = str(script)
			break

	raw_data = script.split('latlons":[')[-1].replace("\\","").replace("u00ae","").replace('"','').split("]]")[0].strip()
	items = raw_data.split("]")

	locator_domain = "amstargas.com"

	for item in items:
		item = BeautifulSoup(item.replace(",[","["),"lxml")
		location_name = item.p.text.split(",")[3].replace("  "," ").strip()

		street_address = item.find(class_="street-address").text.replace("South South","South").strip()
		if street_address == "West Ogden Avenue":
			street_address = "3939 West Ogden Ave"
		city = item.find(class_="locality").text.strip()
		state = item.find(class_="region").text.split(",")[-1].strip()
		zip_code = item.find(class_="postal-code").text.strip()
		country_code = "US"
		store_number = item.p.text.split(",")[2]
		location_type = str(item).split("</strong>")[-1].split("</p>")[0]
		if "html" in location_type:
			location_type = "<MISSING>"
		phone = "<MISSING>"
		hours_of_operation = "<MISSING>"
		latitude = item.p.text.split(",")[0].replace("[","")
		longitude = item.p.text.split(",")[1]
		link = "https://www.amstargas.com" + item.a['href']

		if "county" in state.lower():
			req = session.get(link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")
			state = base.find(class_="field-items").text.split(",")[-1].strip()[:3].strip()
		if state == "Ill":
			state = "IL"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
