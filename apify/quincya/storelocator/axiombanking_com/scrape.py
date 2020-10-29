from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('axiombanking_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.axiombanking.com/about-us/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	locator_domain = "axiombanking.com"

	script = base.find(id="location_finder-js-extra").text.strip()
	
	js = base.text.split("location_Finder = {")[1].split('location_coordinates":')[1].split(',"location_titles')[0].strip()
	coords = json.loads(js)
	
	js = base.text.split('location_titles":')[1].split(',"location_desc')[0].strip()
	titles = json.loads(js)
	
	js = base.text.split('location_desc":')[1].split(',"location_types')[0].strip()
	details = json.loads(js)

	for i in range(len(coords)):
		location_name = titles[i]['title']
		# logger.info(location_name)
		item = BeautifulSoup(details[i]['info'],"lxml")		
		if "," in item.p.text:
			raw_address = item.p.text.split('\n')
			phone = item.find_all("p")[1].text.replace("Phone:","").strip()
			hours_of_operation = item.find_all("p")[2].text.replace("\n"," ").strip()
		else:
			raw_address = item.find_all("p")[1].text.split('\n')
			phone = item.find_all("p")[2].text.replace("Phone:","").strip()
			hours_of_operation = item.find_all("p")[3].text.replace("\n"," ").strip()

		street_address = raw_address[0]
		city = raw_address[1].split(",")[0]
		state = raw_address[1].split(",")[1].split()[0]
		zip_code = raw_address[1].split(",")[1].split()[1]
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		latitude = coords[i]['lat']
		longitude = coords[i]['lng']

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
