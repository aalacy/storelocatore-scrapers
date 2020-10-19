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
	
	base_link = "https://www.google.com/maps/d/u/0/embed?mid=1sZTkkQYMYLcUr_JcKmiZYnzyhZUZd1K7&hl=en&ll=39.33374792734868%2C-75.34473837866054&z=8"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	script = str(base.find('script'))

	raw_data1 = script.split('null,[[[')[-2].split('https')[0].replace("\\","").replace('"','').strip()
	raw_data2 = script.split('null,null,null,null,null')[-1].split('https')[0].replace("\\","").replace('"','').strip()

	items = raw_data1.split(",[[[")[1:-1] + raw_data2.split(",[[[")[1:-1]

	locator_domain = "carrollfuel_com"

	for item in items:
		if "City" not in item:
			continue
		location_name = item.split("Station Name,[")[-1].split("]")[0].replace("u0027","'").encode("ascii", "ignore").decode().strip()
		if "High" in location_name[:10]:
			continue
		street_address = item.split("Addresses,[")[-1].split("]")[0].replace("u0027","'").encode("ascii", "ignore").decode().strip()
		city = item.split("City,[")[-1].split("]")[0].replace("u0027","'").strip()
		state = item.split("State,[")[-1].split("]")[0].strip()
		zip_code = item.split("Zip code,[")[-1].split("]")[0].strip().split(",")[-1].replace(".0","")
		country_code = "US"
		store_number = "<MISSING>"
		if "Fuel" in location_name:
			location_type = "Carroll Fuel"
		else:
			location_type = "<MISSING>"
		phone = "<MISSING>"
		hours_of_operation = "<MISSING>"

		geo = re.findall(r'[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+',item)[0].split(",")
		latitude = geo[0]
		longitude = geo[1]

		data.append([locator_domain, "<MISSING>", location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
