from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
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
	
	base_link = "https://www.pakmail.com/store-locator?origin=NY&lat=40.7127753&long=-74.0059728&distance[search_distance]=5000&Submit=Find+Now"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	all_scripts = base.find_all('script')
	for script in all_scripts:
		if '"markers":' in str(script):
			script = str(script)
			break
	
	all_links = []	
	ids = re.findall(r'us[0-9]+', script)
	
	for id_ in ids:
		link = "https://www.pakmail.com/" + id_
		if link not in all_links:
			all_links.append(link)

	data = []
	locator_domain = "pakmail.com"

	for link in all_links:
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		try:
			script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
		except:
			continue
		store = json.loads(script)

		location_name = store['name']
		street_address = store['address']['streetAddress'].replace("Shopping Center","").split("(")[0].strip()
		city = store['address']['addressLocality']
		state = "<MISSING>"
		zip_code = store['address']['postalCode']
		if len(zip_code) < 5:
			zip_code = "0" + zip_code

		country_code = "US"
		store_number = link.split("/")[-1].split("us")[1]
		location_type = "<MISSING>"
		phone = store['telephone']

		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']

		hours_of_operation = " ".join(list(base.find(class_="hours").stripped_strings))
		final_link = store['url']

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
