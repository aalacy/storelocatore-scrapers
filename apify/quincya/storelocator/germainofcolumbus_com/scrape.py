from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
from sgselenium import SgChrome
import json
import time


def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.germainofcolumbus.com/locations/index.htm"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	driver = SgChrome().chrome()
	time.sleep(2)

	data = []

	items = base.find(id="proximity-dealer-list").find_all(class_="vcard")
	locator_domain = "germainofcolumbus.com"

	for item in items:

		location_name = item.a.text.strip()

		street_address = item.find(class_="street-address").text.strip()
		city = item.find(class_="locality").text.strip()
		state = item.find(class_="region").text.strip()
		zip_code = item.find(class_="postal-code").text.strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		latitude = item.find(class_="latitude").text.strip()
		longitude = item.find(class_="longitude").text.strip()

		link = item.a["href"]
		if link:
			driver.get(link)
			time.sleep(5)

			base = BeautifulSoup(driver.page_source,"lxml")

			phone = base.find(class_="tel phone1 collapsed-show")["data-click-to-call-phone"]

			fin_script = ""
			all_scripts = base.find_all('script')
			for script in all_scripts:
					if "window.DDC.browserSunsetData" in str(script):
							fin_script = str(script)
							break

			days = json.loads(fin_script.split('"hours":')[1].split(",\n")[0].strip())
			hours_of_operation = ""
			for day in days:
				hours_of_operation = (hours_of_operation + " " + day.title() + " " + days[day]["value"]).strip()
		else:
			phone = "<MISSING>"
			if location_name == "Toyota West":
				phone = "8004211512"
			link = "<MISSING>"
			hours_of_operation = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
