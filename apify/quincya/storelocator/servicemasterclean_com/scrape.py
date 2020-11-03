from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('servicemasterclean_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = 'https://www.servicemasterclean.com/locations/location-list/'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	all_links = []
	found_poi = []

	items = base.find(id="LocationList_HDR0_State").find_all("option")[1:]
	locator_domain = "servicemasterclean.com"

	for item in items:
		all_links.append("https://www.servicemasterclean.com/locations/" + item.text.replace(" ","-").lower())

	for link in all_links:
		logger.info(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		items = base.find_all(class_="third")
		for item in items:
			raw_data = item.text.split("\n")

			location_name = item.strong.text.strip()

			raw_address = list(item.address.stripped_strings)
			street_address = " ".join(raw_address[:-1]).replace("\r\n","").replace("\t","").replace("\xa0"," ").strip()
			if not street_address:
				street_address = "<MISSING>"
			city = raw_address[-1].split(",")[0].strip()
			state = raw_address[-1].split(",")[1][:-6].strip()
			zip_code = raw_address[-1][-6:].strip()
			country_code = "US"
			location_type = "<MISSING>"
			phone = item.find(class_="flex phone-contact").text.strip()
			hours_of_operation = "<MISSING>"
			latitude = "<MISSING>"
			longitude = "<MISSING>"
			link = "https://www.servicemasterclean.com" + item.find(class_="text-btn")["href"]
			
			if link in found_poi:
				continue
			req = session.get(link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")

			if "COMING SOON" in base.h1.text.upper():
				continue

			try:
				store_number = base.find(class_="box")["data-key"]
			except:
				store_number = "<MISSING>"

			hours_of_operation = "<MISSING>"
			try:
				if base.find(id="HoursContainer").text.strip():
					try:
						payload = {'_m_': 'HoursPopup',
									'HoursPopup$_edit_': store_number}

						response = session.post(link,headers=HEADERS,data=payload)
						hr_base = BeautifulSoup(response.text,"lxml")
						hours_of_operation = " ".join(list(hr_base.table.stripped_strings))
					except:
						hours_of_operation = "<MISSING>"
			except:
				pass

			found_poi.append(link)
			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
