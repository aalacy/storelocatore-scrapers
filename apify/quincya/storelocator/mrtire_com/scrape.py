from bs4 import BeautifulSoup
from sgselenium import SgChrome
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
	
	base_link = 'https://www.mrtire.com/store-search/?redirect=%2F'

	driver = SgChrome().chrome()
	driver.get(base_link)

	base = BeautifulSoup(driver.page_source,"lxml")

	data = []

	items = base.find_all(class_="results-store-container")
	locator_domain = "mrtire.com"

	for item in items:
		location_name = item.find(class_="results-store-header").text.strip() + " " + item.p.text.strip()
		
		street_address = item.find(class_="results-store-info").div.text.strip()
		city_line = item.find(class_="results-store-info").find_all('div')[1].text.strip().split(",")
		city = city_line[0].strip()
		state = city_line[-1].strip().split()[0].strip()
		zip_code = city_line[-1].strip().split()[1].strip()

		country_code = "US"
		store_number = item.p.text.split("#")[1]
		
		location_type = "<MISSING>"
		phone = item.find(class_="results-store-phone").text.strip()
		hours_of_operation = " ".join(list(item.find(class_="results-store-hours-list").stripped_strings))

		geo = item.find(class_="results-directions-link")['href'].split("=")[-1].split(",")
		latitude = geo[0]
		longitude = geo[1]
		link = "https://www.mrtire.com/appointment?storeid=" + store_number
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
