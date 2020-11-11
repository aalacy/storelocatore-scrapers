from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('oakstreethealth_com')


def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.oakstreethealth.com/locations/all"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	all_links = []
	locator_domain = "oakstreethealth.com"

	items = base.find_all(class_="thumb__content")
	for item in items:

		street_address = item.find(class_="thumb__text type-body").text.strip()
		city = item.a.text.split("|")[1].split(",")[0].strip()
		state = item.a.text.split("|")[1].split(",")[1].strip()
		
		country_code = "US"
		store_number = "<MISSING>"

		link = item.a["href"]
		logger.info(link)
		
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		
		location_name = base.h1.text.strip()

		zip_code = base.find(class_="icon-title__text flex flex-col items-start").text.split("Get Directions")[0].split()[-1].strip()
		if len(zip_code) == 4:
			zip_code = "0" + zip_code

		try:
			raw_types = base.find_all(class_="feature-grid section section--featureGrid")[1].find_all(class_="icon-title__text")
			location_type = ""
			for raw_type in raw_types:
				location_type = location_type + "," + raw_type.text.strip()
			location_type = location_type[1:].strip()
		except:
			location_type = "<MISSING>"

		phone = base.find_all(class_="icon-title__text")[1].text.strip()
		try:
			hours_of_operation = base.find(class_="w-full w-3/4@large pt-2").text.replace("\n\n\n"," ").replace("\n"," ").strip()
		except:
			hours_of_operation = "<MISSING>"

		try:
			map_url = base.find(rel="noopener noreferrer")["href"]
			req = session.get(map_url, headers = HEADERS)
			map_link = req.url
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()

			if len(latitude) > 20:
				req = session.get(map_url, headers = HEADERS)
				maps = BeautifulSoup(req.text,"lxml")

				try:
					raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
					latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
					longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
				except:
					latitude = "<MISSING>"
					longitude = "<MISSING>"
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"
		if street_address == "2240 East 53rd St Suite B-1":
			latitude = "39.849198"
			longitude = "-86.12594"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
